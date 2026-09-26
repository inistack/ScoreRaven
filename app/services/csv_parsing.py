import csv
import io

class CSVParseError(Exception):
    pass

def extract_emails_from_csv(file_storage):
    try:
        raw = file_storage.read().decode("utf-8")
    except UnicodeDecodeError:
        raise CSVParseError("File must be UTF-8 encoded.")

    if not raw.strip():
        raise CSVParseError("The CSV file is empty.")

    try:
        has_header = csv.Sniffer().has_header(raw[:2048])
    except csv.Error:
        has_header = False

    emails = []

    if has_header:
        reader = csv.DictReader(io.StringIO(raw))
        email_column = _find_email_column(reader.fieldnames)

        if email_column is None:
            raise CSVParseError(
                "Couldn't find an 'email' column in the file header. "
                f"Found columns: {', '.join(reader.fieldnames or [])}"
            )

        for row in reader:
            value = (row.get(email_column) or "").strip()
            if "@" in value:
                emails.append(value)
    else:
        reader = csv.reader(io.StringIO(raw))
        for row in reader:
            if not row:
                continue
            value = row[0].strip()
            if "@" in value:
                emails.append(value)

    if not emails:
        raise CSVParseError("No valid email addresses found in the file.")

    return emails


def _normalize_header(name):
    return name.strip().lower().replace(" ", "").replace("-", "").replace("_", "")


def _find_email_column(fieldnames):
    if not fieldnames:
        return None

    exact_matches = {"email", "emailaddress", "emailid", "e mail"}

    for name in fieldnames:
        if not name:
            continue
        normalized = _normalize_header(name)
        if normalized in exact_matches or normalized.endswith("email"):
            return name

    return None