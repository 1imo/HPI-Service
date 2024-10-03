import json
from curl_cffi import requests
import time
import random
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class AutoTraderAPI:
    def __init__(self):
        self.base_url = "https://www.autotrader.co.uk"
        
        # Print environment variables
        print("USER_AGENT:", os.getenv("USER_AGENT"))
        print("SAURON_APP_VERSION:", os.getenv("SAURON_APP_VERSION"))
        print("SP_ID:", os.getenv("SP_ID"))
        print("AB_TEST_GROUPS:", os.getenv("AB_TEST_GROUPS"))
        print("POSTCODE:", os.getenv("POSTCODE"))
        print("SP:", os.getenv("SP"))
        
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "www.autotrader.co.uk",
            "Origin": "https://www.autotrader.co.uk",
            "Referer": "https://www.autotrader.co.uk/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": os.getenv("USER_AGENT"),
            "x-sauron-app-name": "sauron-search-results-app",
            "x-sauron-app-version": os.getenv("SAURON_APP_VERSION")
        }
        self.cookies = {
            "_sp_id.05b0": os.getenv("SP_ID"),
            "_sp_ses.05b0": "*",
            "abTestGroups": os.getenv("AB_TEST_GROUPS"),
            "acceptATCookies": "true",
            "at_sp_consent": "true",
            "postcode": os.getenv("POSTCODE"),
            "sp": os.getenv("SP"),
        }

    def _make_request(self, url, payload):
        print(self.headers)
        response = requests.post(url, headers=self.headers, cookies=self.cookies, json=payload)


        response.raise_for_status()
        return response.json()

    def _generate_query_fields(self, fields, depth=0, max_depth=5):
        if depth > max_depth:
            return ""
        
        query = ""
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            
            if field_type['kind'] == 'OBJECT' and field_type['name'] != 'String':
                subfields = self._get_subfields(field_type['name'])
                query += f"{field_name} {{ {self._generate_query_fields(subfields, depth+1, max_depth)} }}\n"
            else:
                query += f"{field_name}\n"
        
        return query

    def _get_subfields(self, type_name):
        schema_query = f"""
        query {{
          __type(name: "{type_name}") {{
            fields {{
              name
              type {{
                name
                kind
                ofType {{
                  name
                  kind
                }}
              }}
            }}
          }}
        }}
        """
        
        print("MAKING QUERY")
        schema_payload = [{"query": schema_query}]
        schema_data = self._make_request(f"{self.base_url}/at-graphql?opname=SchemaQuery", schema_payload)

        print(schema_data)
        
        return schema_data[0]['data']['__type']['fields']

    def _get_full_query(self, type_name):
        schema_query = f"""
        query {{
          __type(name: "{type_name}") {{
            name
            fields {{
              name
              type {{
                name
                kind
                ofType {{
                  name
                  kind
                }}
              }}
            }}
          }}
        }}
        """
        
        schema_payload = [{"query": schema_query}]
        schema_data = self._make_request(f"{self.base_url}/at-graphql?opname=SchemaQuery", schema_payload)
        
        fields = schema_data[0]['data']['__type']['fields']
        query_fields = self._generate_query_fields(fields)
        print(query_fields)
        
        return query_fields

    def search_listings(self, make, model, min_year=None, max_year=None, sample_size=100):
        url = f"{self.base_url}/at-gateway?opname=SearchResultsListingsQuery&opname=SearchResultsFacetsWithGroupsQuery"
        
        # Get the schema for SearchListing type
        schema_query = """
        query {
          __type(name: "SearchListing") {
            name
            fields {
              name
              type {
                name
                kind
                ofType {
                  name
                  kind
                }
              }
            }
          }
        }
        """
        
        schema_payload = [{"query": schema_query}]
        schema_data = self._make_request(f"{self.base_url}/at-graphql?opname=SchemaQuery", schema_payload)
        
        # Generate the query dynamically based on the schema
        query_fields = self._get_full_query("SearchListing")
        
        filters = [
            {"filter": "make", "selected": [make]},
            {"filter": "model", "selected": [model]},
            {"filter": "postcode", "selected": ["NG12 4GJ"]},
            {"filter": "price_search_type", "selected": ["total"]}
        ]

        if min_year:
            filters.append({"filter": "min_year_manufactured", "selected": [str(min_year)]})
        if max_year:
            filters.append({"filter": "max_year_manufactured", "selected": [str(max_year)]})

        all_listings = []
        
        def fetch_page(page_num, sort_by):
            payload = [{
                "operationName": "SearchResultsListingsQuery",
                "variables": {
                    "filters": filters,
                    "channel": "cars",
                    "page": page_num,
                    "sortBy": sort_by,
                    "listingType": None,
                    "searchId": f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}"
                },
                "query": f"""
                query SearchResultsListingsQuery($filters: [FilterInput!]!, $channel: Channel!, $page: Int, $sortBy: SearchResultsSort, $listingType: [ListingType!], $searchId: String!) {{
                  searchResults(
                    input: {{facets: [], filters: $filters, channel: $channel, page: $page, sortBy: $sortBy, listingType: $listingType, searchId: $searchId}}
                  ) {{
                    listings {{
                      ... on SearchListing {{
                        {query_fields}
                      }}
                    }}
                    page {{
                      number
                      count
                      results {{
                        count
                      }}
                    }}
                    searchInfo {{
                      isForFinanceSearch
                    }}
                    trackingContext {{
                      searchId
                    }}
                  }}
                }}
                """
            }]

            data = self._make_request(url, payload)
            page_info = data[0]['data']['searchResults']['page']
            listings = data[0]['data']['searchResults']['listings']
            return page_info, listings

        first_page_info, first_page_listings = fetch_page(1, "price_asc")
        total_pages = first_page_info['count']

        all_listings.extend(first_page_listings)

        last_page_info, last_page_listings = fetch_page(total_pages, "price_desc")
        all_listings.extend(last_page_listings)

        remaining_samples = sample_size - len(all_listings)
        random_pages_to_fetch = min(remaining_samples // 15, total_pages - 2)

        random_pages = random.sample(range(2, total_pages), random_pages_to_fetch)
        for page in random_pages:
            _, random_page_listings = fetch_page(page, "relevance")
            all_listings.extend(random_page_listings)

            time.sleep(1)

        all_listings = all_listings[:sample_size]

        return all_listings

    def get_listing_stats(self, listings):
        total_listings = len(listings)
        prices = []
        years = []
        mileages = []

        for listing in listings:
            if 'price' in listing and isinstance(listing['price'], (int, float)):
                prices.append(listing['price'])
            elif 'price' in listing and isinstance(listing['price'], str):
                price = float(''.join(filter(str.isdigit, listing['price'])))
                prices.append(price)

            if 'year' in listing:
                years.append(int(listing['year']))

            if 'mileage' in listing and isinstance(listing['mileage'], dict) and 'mileage' in listing['mileage']:
                mileages.append(int(listing['mileage']['mileage']))

        stats = {
            "total_listings": total_listings,
            "price": {
                "min": min(prices) if prices else None,
                "max": max(prices) if prices else None,
                "avg": sum(prices) / len(prices) if prices else None
            },
            "year": {
                "min": min(years) if years else None,
                "max": max(years) if years else None,
                "avg": sum(years) / len(years) if years else None
            },
            "mileage": {
                "min": min(mileages) if mileages else None,
                "max": max(mileages) if mileages else None,
                "avg": sum(mileages) / len(mileages) if mileages else None
            }
        }

        return stats

    def get_advert_details(self, advert_id, number_of_images=100, postcode="NG12 4GJ"):
        url = f"{self.base_url}/at-graphql?opname=FPADataQuery"
        
        query = [
            {
                "operationName": "FPADataQuery",
                "variables": {
                    "advertId": advert_id,
                    "numberOfImages": number_of_images,
                    "searchOptions": {
                        "advertisingLocations": ["at_cars"],
                        "postcode": postcode,
                        "collectionLocationOptions": {"searchPostcode": postcode},
                        "channel": "cars"
                    },
                    "postcode": postcode
                },
                "query": """
                query FPADataQuery($advertId: String!, $numberOfImages: Int, $searchOptions: SearchOptions, $postcode: String) {
                  search {
                    advert(advertId: $advertId, searchOptions: $searchOptions) {
                      id
                      stockItemId
                      isAuction
                      hoursUsed
                      serviceHistory
                      title
                      excludePreviousOwners
                      advertisedLocations
                      dueAtSeller
                      motExpiry
                      motInsurance
                      lastServiceOdometerReadingMiles
                      lastServiceDate
                      warrantyMonthsOnPurchase
                      twelveMonthsMotIncluded
                      heading {
                        title
                        subtitle
                        __typename
                      }
                      attentionGrabber
                      rrp
                      price
                      priceGBX
                      priceExcludingFees
                      priceExcludingFeesGBX
                      suppliedPrice
                      suppliedPriceGBX
                      priceOnApplication
                      plusVatIndicated
                      vatStatus
                      saving
                      noAdminFees
                      adminFee
                      adminFeeInfoDescription
                      dateOfRegistration
                      homeDeliveryRegionCodes
                      capabilities {
                        marketExtensionHomeDelivery {
                          enabled
                          __typename
                        }
                        marketExtensionClickAndCollect {
                          enabled
                          __typename
                        }
                        marketExtensionCentrallyHeld {
                          enabled
                          __typename
                        }
                        marketExtensionOem {
                          enabled
                          __typename
                        }
                        digitalRetailing {
                          enabled
                          __typename
                        }
                        __typename
                      }
                      registration
                      generation {
                        generationId
                        name
                        review {
                          expertReviewSummary {
                            rating
                            reviewUrl
                            __typename
                          }
                          __typename
                        }
                        __typename
                      }
                      hasShowroomProductCode
                      isPartExAvailable
                      isFinanceAvailable
                      isFinanceFullApplicationAvailable
                      financeProvider
                      financeDefaults {
                        term
                        mileage
                        depositAmount
                        __typename
                      }
                      hasFinanceInformation
                      retailerId
                      privateAdvertiser {
                        contact {
                          protectedNumber
                          email
                          __typename
                        }
                        location {
                          town
                          county
                          postcode
                          __typename
                        }
                        tola
                        __typename
                      }
                      advertiserSegment
                      dealer {
                        dealerId
                        description
                        distance
                        stockLevels {
                          atStockCounts {
                            car
                            van
                            __typename
                          }
                          __typename
                        }
                        assignedNumber {
                          number
                          __typename
                        }
                        awards {
                          isWinner2018
                          isWinner2019
                          isWinner2020
                          isWinner2021
                          isWinner2022
                          isWinner2023
                          isFinalist2018
                          isFinalist2019
                          isFinalist2020
                          isFinalist2021
                          isFinalist2022
                          isFinalist2023
                          isHighlyRated2018
                          isHighlyRated2019
                          isHighlyRated2020
                          isHighlyRated2021
                          isHighlyRated2022
                          isHighlyRated2023
                          isHighlyRated2024
                          __typename
                        }
                        branding {
                          accreditations {
                            name
                            __typename
                          }
                          brands {
                            name
                            imageUrl
                            __typename
                          }
                          __typename
                        }
                        capabilities {
                          instantMessagingChat {
                            enabled
                            provider
                            __typename
                          }
                          instantMessagingText {
                            enabled
                            provider
                            overrideSmsNumber
                            __typename
                          }
                          __typename
                        }
                        reviews {
                          numberOfReviews
                          overallReviewRating
                          __typename
                        }
                        location {
                          addressOne
                          addressTwo
                          town
                          county
                          postcode
                          latLong
                          __typename
                        }
                        marketing {
                          profile
                          brandingBanner {
                            href
                            __typename
                          }
                          __typename
                        }
                        media {
                          email
                          dealerWebsite {
                            href
                            __typename
                          }
                          phoneNumber1
                          phoneNumber2
                          protectedNumber
                          __typename
                        }
                        name
                        servicesOffered {
                          sellerPromise {
                            monthlyWarranty
                            minMOTAndService
                            daysMoneyBackGuarantee
                            moneyBackRemoteOnly
                            __typename
                          }
                          services
                          products
                          safeSelling {
                            bulletPoints
                            paragraphs
                            __typename
                          }
                          videoWalkAround {
                            bulletPoints
                            paragraphs
                            __typename
                          }
                          nccApproved
                          isHomeDeliveryProductEnabled
                          isPartExAvailable
                          hasSafeSelling
                          hasHomeDelivery
                          hasVideoWalkAround
                          additionalLinks {
                            title
                            href
                            __typename
                          }
                          __typename
                        }
                        __typename
                      }
                      video {
                        url
                        preview
                        __typename
                      }
                      spin {
                        url
                        preview
                        __typename
                      }
                      imageList(limit: $numberOfImages) {
                        nextCursor
                        size
                        images {
                          url
                          templated
                          autotraderAllocated
                          classificationTags {
                            label
                            category
                            __typename
                          }
                          __typename
                        }
                        __typename
                      }
                      priceIndicatorRating
                      priceIndicatorRatingLabel
                      priceDeviation
                      mileageDeviation
                      mileage {
                        mileage
                        unit
                        __typename
                      }
                      plate
                      year
                      vehicleCheckId
                      vehicleCheckStatus
                      vehicleCheckSummary {
                        type
                        title
                        performed
                        writeOffCategory
                        checks {
                          key
                          failed
                          advisory
                          critical
                          warning
                          __typename
                        }
                        __typename
                      }
                      sellerName
                      sellerType
                      sellerProducts
                      sellerLocation
                      sellerLocationDistance {
                        unit
                        value
                        __typename
                      }
                      sellerContact {
                        phoneNumberOne
                        phoneNumberTwo
                        protectedNumber
                        byEmail
                        __typename
                      }
                      description
                      colour
                      manufacturerApproved
                      insuranceWriteOffCategory
                      owners
                      keys
                      vehicleCondition {
                        tyreCondition
                        interiorCondition
                        bodyCondition
                        __typename
                      }
                      specification {
                        isCrossover
                        operatingType
                        emissionClass
                        co2Emissions {
                          co2Emission
                          unit
                          __typename
                        }
                        topSpeed {
                          topSpeed
                          __typename
                        }
                        minimumKerbWeight {
                          weight
                          unit
                          __typename
                        }
                        endLayout
                        trailerAxleNumber
                        bedroomLayout
                        grossVehicleWeight {
                          weight
                          unit
                          __typename
                        }
                        capacityWeight {
                          weight
                          unit
                          __typename
                        }
                        liftingCapacity {
                          weight
                          unit
                          __typename
                        }
                        operatingWidth {
                          width
                          unit
                          __typename
                        }
                        maxReach {
                          length
                          unit
                          __typename
                        }
                        wheelbase
                        berth
                        bedrooms
                        engine {
                          power {
                            enginePower
                            unit
                            __typename
                          }
                          sizeLitres
                          sizeCC
                          manufacturerEngineSize
                          __typename
                        }
                        exteriorWidth {
                          width
                          unit
                          __typename
                        }
                        exteriorLength {
                          length
                          unit
                          __typename
                        }
                        exteriorHeight {
                          height
                          unit
                          __typename
                        }
                        capacityWidth {
                          width
                          unit
                          __typename
                        }
                        capacityLength {
                          length
                          unit
                          __typename
                        }
                        capacityHeight {
                          height
                          unit
                          __typename
                        }
                        seats
                        axleConfig
                        ulezCompliant
                        doors
                        bodyType
                        cabType
                        rawBodyType
                        fuel
                        transmission
                        style
                        subStyle
                        make
                        model
                        trim
                        optionalFeatures {
                          description
                          category
                          __typename
                        }
                        standardFeatures {
                          description
                          category
                          __typename
                        }
                        driverPosition
                        battery {
                          capacity {
                            capacity
                            unit
                            __typename
                          }
                          usableCapacity {
                            capacity
                            unit
                            __typename
                          }
                          range {
                            range
                            unit
                            __typename
                          }
                          charging {
                            quickChargeTime
                            chargeTime
                            __typename
                          }
                          __typename
                        }
                        techData {
                          co2Emissions
                          fuelConsumptionCombined
                          fuelConsumptionExtraUrban
                          fuelConsumptionUrban
                          insuranceGroup
                          minimumKerbWeight
                          zeroToSixtyMph
                          zeroToSixtyTwoMph
                          cylinders
                          valves
                          enginePower
                          topSpeed
                          engineTorque
                          vehicleHeight
                          vehicleLength
                          vehicleWidth
                          wheelbase
                          fuelTankCapacity
                          grossVehicleWeight
                          luggageCapacitySeatsDown
                          bootspaceSeatsUp
                          minimumKerbWeight
                          vehicleWidthInclMirrors
                          maxLoadingWeight
                          standardFeatures {
                            description
                            category
                            __typename
                          }
                          chargingData {
                            fastestChargingPower
                            fastestChargingDuration
                            chargers {
                              description
                              fullCharge {
                                duration
                                endBatteryPercentage
                                __typename
                              }
                              topUp {
                                milesRange
                                duration
                                __typename
                              }
                              chargerLocation
                              milesRangePerHourChargeTime
                              __typename
                            }
                            __typename
                          }
                          __typename
                        }
                        annualTax {
                          standardRate
                          __typename
                        }
                        oemDrivetrain
                        bikeLicenceType
                        derivativeId
                        frameSizeCM
                        frameMaterial
                        frameStyle
                        suspensionType
                        gearShifter
                        brakeType
                        motorMake
                        chargeTimeMinutes
                        numberOfGears
                        tyreDiameterInches
                        driveTrain
                        torque {
                          torque
                          unit
                          __typename
                        }
                        range {
                          totalRange
                          unit
                          __typename
                        }
                        __typename
                      }
                      stockType
                      condition
                      finance {
                        monthlyPayment
                        representativeApr
                        __typename
                      }
                      locationArea(postcode: $postcode) {
                        code
                        region
                        areaOfInterest {
                          postCode
                          manufacturerCodes
                          __typename
                        }
                        __typename
                      }
                      reservation {
                        status
                        eligibility
                        feeCurrency
                        feeInFractionalUnits
                        __typename
                      }
                      __typename
                    }
                    __typename
                  }
                }
                """
            }
        ]

        data = self._make_request(url, query)
        return data[0]['data']['search']['advert']
    
    def get_full_advert_details(self, advert_id, number_of_images=100, postcode="NG12 4GJ"):
        url = f"{self.base_url}/at-graphql?opname=FullAdvertDetailsQuery"
        
        # Get the schema for Advert type
        schema_query = """
        query {
          __type(name: "Advert") {
            name
            fields {
              name
              type {
                name
                kind
                ofType {
                  name
                  kind
                }
              }
            }
          }
        }
        """
        
        schema_payload = [{"query": schema_query}]
        schema_data = self._make_request(f"{self.base_url}/at-graphql?opname=SchemaQuery", schema_payload)
        
        # Generate the query dynamically based on the schema
        query_fields = self._get_full_query("Advert")
        
        query = [
            {
                "operationName": "FullAdvertDetailsQuery",
                "variables": {
                    "advertId": advert_id,
                    "numberOfImages": number_of_images,
                    "searchOptions": {
                        "advertisingLocations": ["at_cars"],
                        "postcode": postcode,
                        "collectionLocationOptions": {"searchPostcode": postcode},
                        "channel": "cars"
                    },
                    "postcode": postcode
                },
                "query": f"""
                query FullAdvertDetailsQuery($advertId: String!, $numberOfImages: Int, $searchOptions: SearchOptions, $postcode: String) {{
                  search {{
                    advert(advertId: $advertId, searchOptions: $searchOptions) {{
                      {query_fields}
                    }}
                  }}
                }}
                """
            }
        ]

        data = self._make_request(url, query)
        return data[0]['data']['search']['advert']

if __name__ == "__main__":
    api = AutoTraderAPI()
    
   
    details = api.get_advert_details("202409113902603")
    full_details = api.get_full_advert_details("202409113902603")
    print(full_details)