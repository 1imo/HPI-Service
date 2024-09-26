import json
from curl_cffi import requests
import time
import random
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file in the parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class AutoTraderAPIError(Exception):
    pass

class AutoTraderAPI:
    def __init__(self):
        # Initialize API with base URL, headers, and cookies
        self.base_url = "https://www.autotrader.co.uk"
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
        # Helper method to make API requests with retry logic
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=self.headers, cookies=self.cookies, json=payload, impersonate="safari15_5")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise AutoTraderAPIError(f"Request failed after {max_retries} attempts: {str(e)}")
                time.sleep(retry_delay * (2 ** attempt) + random.uniform(0, 1))

    def search_listings(self, make, model, min_year=None, max_year=None, sample_size=100):
        # Method to search for vehicle listings
        # 1. Construct the API request URL and payload
        # 2. Fetch the first page (lowest price) and last page (highest price)
        # 3. Calculate and fetch additional random pages to meet the sample size
        # 4. Return the collected listings
        url = f"{self.base_url}/at-gateway?opname=SearchResultsListingsQuery&opname=SearchResultsFacetsWithGroupsQuery"
        
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
                "query": """
                query SearchResultsListingsQuery($filters: [FilterInput!]!, $channel: Channel!, $page: Int, $sortBy: SearchResultsSort, $listingType: [ListingType!], $searchId: String!) {
                  searchResults(
                    input: {facets: [], filters: $filters, channel: $channel, page: $page, sortBy: $sortBy, listingType: $listingType, searchId: $searchId}
                  ) {
                    listings {
                      ... on SearchListing {
                        type
                        advertId
                        title
                        subTitle
                        attentionGrabber
                        price
                        bodyType
                        viewRetailerProfileLinkLabel
                        approvedUsedLogo
                        nearestCollectionLocation: collectionLocations(limit: 1) {
                          distance
                          town
                          __typename
                        }
                        distance
                        discount
                        description
                        images
                        location
                        numberOfImages
                        priceIndicatorRating
                        rrp
                        manufacturerLogo
                        sellerType
                        sellerName
                        dealerLogo
                        dealerLink
                        dealerReview {
                          overallReviewRating
                          numberOfReviews
                          dealerProfilePageLink
                          __typename
                        }
                        fpaLink
                        hasVideo
                        has360Spin
                        hasDigitalRetailing
                        mileageText
                        yearAndPlateText
                        specs
                        finance {
                          monthlyPrice {
                            priceFormattedAndRounded
                            __typename
                          }
                          quoteSubType
                          representativeExample
                          representativeValues {
                            financeKey
                            financeValue
                            __typename
                          }
                          disclaimerText {
                            components {
                              ... on FinanceListingDisclaimerTextComponent {
                                text
                                __typename
                              }
                              ... on FinanceListingDisclaimerLinkComponent {
                                text
                                link
                                __typename
                              }
                              __typename
                            }
                            __typename
                          }
                          financeListingProvider
                          __typename
                        }
                        badges {
                          type
                          displayText
                          __typename
                        }
                        sellerId
                        position
                        trackingContext {
                          retailerContext {
                            id
                            __typename
                          }
                          advertContext {
                            id
                            advertiserId
                            advertiserType
                            make
                            model
                            vehicleCategory
                            year
                            condition
                            price
                            searchVersionId
                            __typename
                          }
                          card {
                            category
                            subCategory
                            pageNumber
                            position
                            __typename
                          }
                          advertCardFeatures {
                            condition
                            numImages
                            hasFinance
                            priceIndicator
                            isManufacturedApproved
                            isFranchiseApproved
                            __typename
                          }
                          distance {
                            distance
                            distance_unit
                            __typename
                          }
                          __typename
                        }
                        __typename
                      }
                      ... on GPTListing {
                        type
                        targetingSegments {
                          name
                          values
                          __typename
                        }
                        areaOfInterest {
                          manufacturerCodes
                          __typename
                        }
                        posId
                        __typename
                      }
                      ... on PreLaunchMarketingListing {
                        type
                        trackingLabel
                        targetUrl
                        title
                        callToActionText
                        textColor
                        backgroundColor
                        bodyCopy
                        smallPrint
                        vehicleImage {
                          src
                          altText
                          __typename
                        }
                        searchFormTitle
                        __typename
                      }
                      ... on LeasingListing {
                        type
                        advertId
                        title
                        subTitle
                        price
                        viewRetailerProfileLinkLabel
                        leasingGuideLink
                        images
                        numberOfImages
                        dealerLogo
                        dealerLink
                        fpaLink
                        hasVideo
                        has360Spin
                        finance {
                          monthlyPrice {
                            priceFormattedAndRounded
                            __typename
                          }
                          representativeExample
                          initialPayment
                          termMonths
                          mileage
                          __typename
                        }
                        badges {
                          type
                          displayText
                          __typename
                        }
                        policies {
                          roadTax
                          returns
                          delivery
                          __typename
                        }
                        sellerId
                        trackingContext {
                          retailerContext {
                            id
                            __typename
                          }
                          advertContext {
                            id
                            advertiserId
                            advertiserType
                            make
                            model
                            vehicleCategory
                            year
                            condition
                            price
                            searchVersionId
                            __typename
                          }
                          card {
                            category
                            subCategory
                            pageNumber
                            position
                            __typename
                          }
                          advertCardFeatures {
                            condition
                            numImages
                            hasFinance
                            priceIndicator
                            isManufacturedApproved
                            isFranchiseApproved
                            __typename
                          }
                          distance {
                            distance
                            distance_unit
                            __typename
                          }
                          __typename
                        }
                        __typename
                      }
                      __typename
                    }
                    page {
                      number
                      count
                      results {
                        count
                        __typename
                      }
                      __typename
                    }
                    searchInfo {
                      isForFinanceSearch
                      __typename
                    }
                    trackingContext {
                      searchId
                      __typename
                    }
                    __typename
                  }
                }
                """
            }]

            try:
                data = self._make_request(url, payload)
                page_info = data[0]['data']['searchResults']['page']
                listings = data[0]['data']['searchResults']['listings']
                return page_info, listings
            except Exception as e:
                print(f"Error fetching page {page_num}: {str(e)}")
                return None, []

        # Fetch first page (lowest price)
        first_page_info, first_page_listings = fetch_page(1, "price_asc")
        if not first_page_info:
            raise AutoTraderAPIError("Failed to fetch the first page")

        total_pages = first_page_info['count']
        print(f"Total pages: {total_pages}")

        all_listings.extend(first_page_listings)
        print(f"Fetched page 1 of {total_pages} (lowest prices)")

        # Fetch last page (highest price)
        last_page_info, last_page_listings = fetch_page(total_pages, "price_desc")
        all_listings.extend(last_page_listings)
        print(f"Fetched page {total_pages} of {total_pages} (highest prices)")

        # Calculate how many random pages to fetch
        remaining_samples = sample_size - len(all_listings)
        random_pages_to_fetch = min(remaining_samples // 15, total_pages - 2)  # Assuming 15 listings per page

        # Fetch random pages
        random_pages = random.sample(range(2, total_pages), random_pages_to_fetch)
        for page in random_pages:
            _, random_page_listings = fetch_page(page, "relevance")
            all_listings.extend(random_page_listings)
            print(f"Fetched random page {page} of {total_pages}")

            time.sleep(1)  # Add a delay to avoid rate limiting

        # Trim the list to the desired sample size
        all_listings = all_listings[:sample_size]

        return all_listings

    def get_listing_stats(self, listings):
        # Calculate statistics from a list of listings
        # Computes min, max, and average for price, year, and mileage
        total_listings = len(listings)
        prices = []
        years = []
        mileages = []

        for listing in listings:
            if 'price' in listing and isinstance(listing['price'], (int, float)):
                prices.append(listing['price'])
            elif 'price' in listing and isinstance(listing['price'], str):
                try:
                    # Remove non-numeric characters and convert to float
                    price = float(''.join(filter(str.isdigit, listing['price'])))
                    prices.append(price)
                except ValueError:
                    pass

            if 'year' in listing:
                try:
                    years.append(int(listing['year']))
                except ValueError:
                    pass

            if 'mileage' in listing and isinstance(listing['mileage'], dict) and 'mileage' in listing['mileage']:
                try:
                    mileages.append(int(listing['mileage']['mileage']))
                except ValueError:
                    pass

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

    def get_advert_details(self, advert_id):
        # Fetch detailed information for a specific advert
        # Constructs and sends a GraphQL query to get comprehensive details
        url = f"{self.base_url}/at-graphql?opname=FPADataQuery"
        
        payload = [{
            "operationName": "FPADataQuery",
            "variables": {
                "advertId": advert_id,
                "numberOfImages": 100,
                "searchOptions": {
                    "advertisingLocations": ["at_cars"],
                    "postcode": "NG12 4GJ",
                    "collectionLocationOptions": {"searchPostcode": "NG12 4GJ"},
                    "channel": "cars"
                },
                "postcode": "NG12 4GJ"
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
        }]

        try:
            data = self._make_request(url, payload)
            return data[0]['data']['search']['advert']
        except KeyError:
            raise AutoTraderAPIError("Unexpected response format")

# Usage example
if __name__ == "__main__":
    api = AutoTraderAPI()
    
    try:
        # Search for Vauxhall Corsa listings between 2015 and 2020
        listings = api.search_listings(make="Vauxhall", model="Corsa", min_year=2015, max_year=2020)
        print(f"Found {len(listings)} listings")

        # Calculate and print statistics for the found listings
        stats = api.get_listing_stats(listings)
        print("\nListing Statistics:")
        print(json.dumps(stats, indent=2))

        # Fetch and print details for the first listing (if any found)
        if listings:
            first_advert_id = listings[0]['advertId']
            print(listings[0])
            details = api.get_advert_details(first_advert_id)
            # Detailed print statement commented out
            # print(f"\nDetails for advert {first_advert_id}:")
            # print(json.dumps(details, indent=2))

    except AutoTraderAPIError as e:
        print(f"An error occurred: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")