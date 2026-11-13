# Changelog

All notable changes to the **Thermor Onix DHW Plus** Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## [v1.0.6] - 2026-11-13

### Fixed
- **coordinator:** Wrap `get_setup()` and `execute_action_group()` in `asyncio.timeout(30)` and catch `TimeoutError` as `UpdateFailed`, preventing stalled cloud requests from freezing `DataUpdateCoordinator` polling (`6b98f80`).
- **init / config_flow:** Stop calling `client.close()` or `async with OverkizClient(...)` on Home Assistant-managed `async_create_clientsession(hass)` sessions (`6b98f80`).

## [v1.0.5] - 2026-11-09

### Fixed
- **coordinator:** Serialize outgoing Modbus device commands with an `asyncio.Lock` semaphore and a `3.0s` settle delay to prevent uPod gateway saturation (`TIME_OUT_ON_TRANSMITTED_COMMAND` / `PEER_DOWN`) when multiple commands are triggered simultaneously (`f03d38f`, `af43e50`).
- **switch:** Reconcile optimistic switch state with live coordinator data by calling `async_write_ha_state()` in the `finally` block after clearing `_attr_is_on`, preventing UI switches from remaining stuck in an optimistic state if a command fails or times out (`af43e50`).
- **water_heater:** Fix missing `CMD_SET_EXPECTED_SHOWERS` import when adjusting target temperature (`af43e50`).

## [v1.0.4] - 2026-11-09

### Added
- **config_flow:** Implement `async_step_reauth` and `async_step_reauth_confirm` so Home Assistant prompts for credential renewal via UI when `ConfigEntryAuthFailed` is raised (`f7efeaa`).

### Changed
- **config_flow:** Modernize `ThermorOnixOptionsFlowHandler` for Home Assistant 2025.12+ compatibility and use Home Assistant's managed `aiohttp` client session (`async_create_clientsession`) (`f7efeaa`).
- **ci:** Gate GitHub Release creation behind successful HACS and Hassfest validation jobs (`07b469f`).

### Fixed
- **init:** Ensure `OverkizClient` session is cleanly closed if initial setup fails before entry registration (`f7efeaa`).

## [v1.0.3] - 2026-11-08

### Added
- **ci:** Add automated GitHub Release and HACS + Hassfest validation workflows (`b3b8666`, `4611b0f`).
- **brand:** Add official integration brand icon and logo under `custom_components/thermor_onix_custom/brand/` for HACS & Home Assistant 2026.3+ (`730d608`).

### Fixed
- **translations:** Migrate `select` entity option keys (`continuous_24h`, `programmed_slots`, `off_peak_hc`) to `snake_case` to pass strict Hassfest validation (`3ed2bb4`).
- **manifest:** Add `integration_type: "device"`, `categories: ["climate.water_heaters"]`, and sort `manifest.json` keys alphabetically per Hassfest specification (`217a68e`, `a1c238b`).

## [v1.0.2] - 2026-11-08

### Fixed
- **switch:** Use `autoMode` parameter for Eco mode as expected by Thermor Onix hardware and Cozytouch API (`d7b5eef`).
- **water_heater:** Map target temperature dial (`50 °C`–`70 °C`) to expected showers count (`1`–`5`) to comply with double-tank Modbus register requirements (`36c6e4d`).
- **button:** Correct weekday encoding for internal clock synchronization button (`0..6` where `0=Sunday`) (`36c6e4d`).

## [v1.0.1] - 2026-11-07

### Fixed
- **entity / switch:** Fix dynamic entity state updates when polling Overkiz cloud and add optimistic state handling for switches (`9b7cd28`).

## [v1.0.0] - 2026-11-07

### Added
- Initial official release of **Thermor Onix DHW Plus** for Home Assistant with dual-tank telemetry, cumulative energy sensor, operating schedule selector, switches, time slot controls, and clock synchronization (`e1e6fd4`).
