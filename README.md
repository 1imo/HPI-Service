# HPI-Service

My friends and I grew tired of paying CarVertical £15 to check, value, and rank cars. In its current state, it already rivals CarVertical's reports, with information spanning 69 data points (Models/vehicle.py), we are only adding more.

Initially, this was a Discord Bot in our server, but this is a rewrite as a standalone API interface to be consumed by anything as we move forward.

For speed, I opted to reverse-engineer back-end APIs and consume data this way. All data is publicly available except consumable API integrations with eBay and DVSA APIs. The DVSA API might not be required anymore since MOT history is returned by other services in the codebase. The eBay API integration came from the old Discord bot and is likely to be used along the AutoTraderService to sample the market and find similar vehicles for pricing functionality.

Overall, it is a cleaner codebase with a greater outlook on the end goal with the addition of models.
