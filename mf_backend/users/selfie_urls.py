from onboarding_v2.storage import generate_presigned_get


def get_selfie_access_url(selfie_field):
    if not selfie_field:
        return None

    object_name = str(selfie_field)
    try:
        return generate_presigned_get(
            object_name=object_name,
            response_headers={"response-content-disposition": "inline"},
        ).get("get_url")
    except Exception:
        try:
            return selfie_field.url
        except Exception:
            return object_name
