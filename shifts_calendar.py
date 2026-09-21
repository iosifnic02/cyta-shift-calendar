from datetime import datetime, timedelta
from pathlib import Path
import uuid

INPUT_FILE = "shifts.txt"
OUTPUT_FILE = "shifts.ics"


def read_shifts():
    shifts = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                date_text, shift = line.split(",", 1)

                date = datetime.strptime(
                    date_text.strip(),
                    "%d/%m/%Y"
                )

                shift = shift.strip().upper()

                if shift not in {"H", "N", "-"}:
                    raise ValueError(
                        f"Unknown shift '{shift}'"
                    )

                shifts.append((date, shift))

            except Exception as e:
                raise ValueError(
                    f"Error in {INPUT_FILE} line "
                    f"{line_number}: {line}"
                ) from e

    return shifts


def format_ics_datetime(dt):
    return dt.strftime("%Y%m%dT%H%M%S")


def create_event(date, shift):
    if shift == "H":
        start = date.replace(
            hour=7,
            minute=0,
            second=0
        )

        end = date.replace(
            hour=19,
            minute=0,
            second=0
        )

        title = "Day Shift"

    elif shift == "N":
        start = date.replace(
            hour=19,
            minute=0,
            second=0
        )

        end = (
            date + timedelta(days=1)
        ).replace(
            hour=7,
            minute=0,
            second=0
        )

        title = "Night Shift"

    else:
        return None

    # Stable UID based on date + shift.
    # Same shift won't be duplicated when ICS updates.
    uid = (
        f"cyta-{date:%Y%m%d}-{shift}"
        "@shift-calendar"
    )

    return [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{datetime.utcnow():%Y%m%dT%H%M%SZ}",
        (
            "DTSTART;TZID=Europe/Nicosia:"
            f"{format_ics_datetime(start)}"
        ),
        (
            "DTEND;TZID=Europe/Nicosia:"
            f"{format_ics_datetime(end)}"
        ),
        f"SUMMARY:{title}",
        "DESCRIPTION:CYTA Work Shift",
        "STATUS:CONFIRMED",
        "TRANSP:OPAQUE",
        "END:VEVENT"
    ]


def create_calendar(shifts):
    calendar = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//CYTA Shift Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:CYTA Shifts",
        "X-WR-TIMEZONE:Europe/Nicosia",
    ]

    day_count = 0
    night_count = 0

    for date, shift in shifts:
        if shift == "-":
            continue

        event = create_event(
            date,
            shift
        )

        if event:
            calendar.extend(event)

            if shift == "H":
                day_count += 1

            elif shift == "N":
                night_count += 1

    calendar.append(
        "END:VCALENDAR"
    )

    content = "\r\n".join(calendar) + "\r\n"

    Path(OUTPUT_FILE).write_text(
        content,
        encoding="utf-8"
    )

    return day_count, night_count


def main():
    print()
    print("CYTA SHIFT CALENDAR")
    print("----------------------------")

    shifts = read_shifts()

    print(
        f"Loaded {len(shifts)} days "
        f"from {INPUT_FILE}"
    )

    print()
    print("Schedule:")
    print("----------------------------")

    for date, shift in shifts:
        if shift == "H":
            description = "07:00 - 19:00"

        elif shift == "N":
            description = "19:00 - 07:00 next day"

        else:
            description = "OFF"

        print(
            f"{date:%d/%m/%Y} | "
            f"{shift} | {description}"
        )

    day_count, night_count = (
        create_calendar(shifts)
    )

    print()
    print("----------------------------")
    print(f"Day shifts:   {day_count}")
    print(f"Night shifts: {night_count}")
    print(
        f"Total shifts: "
        f"{day_count + night_count}"
    )
    print("----------------------------")

    print()
    print(
        f"Calendar created: {OUTPUT_FILE}"
    )

    print(
        f"Location: "
        f"{Path(OUTPUT_FILE).resolve()}"
    )

    print()


if __name__ == "__main__":
    main()