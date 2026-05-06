"""Read-only setting-group diagnostics for the ABB relay."""

import argparse
from dataclasses import dataclass
from string import printable
from typing import Optional

from .config import RelayConfig
from .modbus import Ref620ModbusClient

DOCUMENTED_SSR2_ADDRESS = 9001
DOCUMENTED_SETTING_GROUP_ADDRESS = 9006
RET615_5X_SETTING_GROUP_ADDRESS = 2300
DEVICE_INFO_ADDRESS = 9000


@dataclass
class SettingGroupProbe:
    source: str
    address: int
    raw_value: int
    decoded_group: Optional[int]
    note: str


def main() -> None:
    args = parse_args()
    config = RelayConfig()
    client = Ref620ModbusClient(config)

    print("REF620/620-Series Setting Group Probe")
    print(f"Host: {config.host}:{config.port} (unit {config.unit_id})")
    print()

    device_info = read_device_info(client)
    print("Device info probe @ 9000:")
    print(device_info)
    if "RET615" in device_info and "REF620" not in device_info:
        print(
            "NOTE: Device info appears to identify a RET615, while this repo uses "
            "REF620 manuals. Measurement reads may overlap, but setting registers "
            "should be verified against the connected relay's exact point list."
        )
    print()

    probes = [
        read_ret615_setting_register(client, RET615_5X_SETTING_GROUP_ADDRESS),
        read_setting_register(client, DOCUMENTED_SETTING_GROUP_ADDRESS),
        read_ssr2_register(client, DOCUMENTED_SSR2_ADDRESS),
        read_ssr2_register(client, DOCUMENTED_SSR2_ADDRESS - 1, source="SSR2 alternate -1"),
    ]

    for probe in probes:
        group_text = (
            str(probe.decoded_group)
            if probe.decoded_group is not None
            else "not a valid 1..6 setting group"
        )
        print(
            f"{probe.source} @ {probe.address}: raw={probe.raw_value} "
            f"decoded={group_text} ({probe.note})"
        )

    valid = [probe for probe in probes if probe.decoded_group is not None]
    print()
    if valid:
        best = valid[0]
        print(
            f"Best read-only candidate: setting group {best.decoded_group} "
            f"from {best.source} @ {best.address}"
        )
    else:
        print(
            "No trustworthy setting-group value was found from the REF620 documented "
            "addresses. Use the connected relay's exact point-list manual before "
            "attempting a write."
        )
        return

    if args.set_group is not None:
        change_setting_group(client, args.set_group, confirmed=args.yes)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read or change the relay active setting group."
    )
    parser.add_argument(
        "--set",
        dest="set_group",
        type=int,
        choices=range(1, 7),
        metavar="1..6",
        help="change the active setting group; requires --yes",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="confirm that you intend to write the setting-group register",
    )
    return parser.parse_args()


def change_setting_group(
    client: Ref620ModbusClient,
    group: int,
    confirmed: bool,
) -> None:
    print()
    print(
        f"Requested change: write setting group {group} to "
        f"address {RET615_5X_SETTING_GROUP_ADDRESS}"
    )
    if not confirmed:
        raise SystemExit(
            "Refusing to write without --yes. Re-run with --yes after confirming "
            "this is the intended relay and setting group."
        )

    client.write_holding_register(RET615_5X_SETTING_GROUP_ADDRESS, group)
    readback = read_ret615_setting_register(client, RET615_5X_SETTING_GROUP_ADDRESS)
    if readback.decoded_group != group:
        raise SystemExit(
            f"Write sent, but readback was {readback.raw_value}; expected {group}."
        )

    print(f"Confirmed active setting group is now {group}.")


def read_device_info(client: Ref620ModbusClient) -> str:
    result = client.read_holding_registers(DEVICE_INFO_ADDRESS, 40)
    data = bytearray()
    for value in result.raw_registers:
        data.append((value >> 8) & 0xFF)
        data.append(value & 0xFF)
    return "".join(chr(byte) if chr(byte) in printable else "." for byte in data).strip(".")


def read_setting_register(
    client: Ref620ModbusClient,
    address: int,
) -> SettingGroupProbe:
    value = client.read_holding_registers(address, 1).raw_registers[0]
    group = value if 1 <= value <= 6 else None
    return SettingGroupProbe(
        source="Parameter Setting Group in Use register",
        address=address,
        raw_value=value,
        decoded_group=group,
        note="REF620 point-list Table 2.1 says this writable u16 register selects the group",
    )


def read_ret615_setting_register(
    client: Ref620ModbusClient,
    address: int,
) -> SettingGroupProbe:
    value = client.read_holding_registers(address, 1).raw_registers[0]
    group = value if 1 <= value <= 6 else None
    return SettingGroupProbe(
        source="RET615 5.x active setting group register",
        address=address,
        raw_value=value,
        decoded_group=group,
        note=(
            "RET615 5.0 FP1 ANSI point list shows RegA 2301; pymodbus uses "
            "zero-based address 2300"
        ),
    )


def read_ssr2_register(
    client: Ref620ModbusClient,
    address: int,
    source: str = "SSR2 active-group bits",
) -> SettingGroupProbe:
    value = client.read_holding_registers(address, 1).raw_registers[0]
    group = decode_group_from_ssr2(value)
    high_bits = value & 0xF800
    note = "bits 3..5 per 620-series protocol manual Table 15"
    if high_bits:
        note += "; high reserved bits are set, so this is probably not SSR2"
        group = None
    return SettingGroupProbe(
        source=source,
        address=address,
        raw_value=value,
        decoded_group=group,
        note=note,
    )


def decode_group_from_ssr2(value: int) -> Optional[int]:
    group = (value >> 3) & 0b111
    return group if 1 <= group <= 6 else None


if __name__ == "__main__":
    main()
