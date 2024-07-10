
# Skomer Checker: Check avalibility of sailing to land on Skomer

A very simple and probably flaky integration to find the first avaliable sailing to land on Skomer meeting certain requirements

## Installation

### HACS

1. Search for and download the "Cardiff Waste" integration
2. Restart your Home Assistant
3. Follow the [setup](#setup) instructions below

### Manual 

1. Copy the `skomer` folder from this repository to the `custom_components` repository in your Home Assistant's configuration directory (the same place as your `configuration.yaml`)
2. Restart you Home Assistant
3. Follow the [setup](#setup) instructions below

### Setup

For ease you can skip the first two steps using this my.home-assistant link:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=skomer)

1. Go to Devices & Services in Configuration
2. Click Add Integration and select Skomer Checker
3. When prompted select how many days into the future you wish to check, minimum avaliability your require (i.e. the number of people in your party) and whether to check all days or only weekends. Note that since sailings only take place on Monday if it is bank holiday, Mondays are coutned as weekends.
