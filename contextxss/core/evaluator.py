from concurrent.futures import ThreadPoolExecutor, as_completed
from contextxss.core.requester import send_request
from contextxss.core.reflector import detect_reflection


def evaluate_payloads(
    url: str, method: str, data: str,
    payloads: list[dict], context: str,
    timeout: int, proxies: dict = None
) -> list[dict]:
    """
    Sends each payload and evaluates if it was successfully reflected/unescaped.
    Uses concurrency for speed, caching to avoid duplicates, and early stopping.
    """
    results = []
    seen_payloads = set()

    def test_payload(p_dict):
        payload_str = p_dict["payload"]

        status, headers, response_text, req_url, req_data = send_request(
            url, method, data, payload_str, timeout, proxies
        )

        result = {
            "payload": payload_str,
            "explanation": p_dict.get("explanation", ""),
            "confidence": p_dict.get("confidence", "Low"),
            "success": False,
            "reason": ""
        }

        if status is None:
            result["reason"] = "Request failed or timed out"
            return result

        is_reflected, positions = detect_reflection(response_text, payload_str)

        if is_reflected:
            # Heuristic Accuracy Check:
            # If the payload doesn't contain dangerous breakout characters for its
            # context, a literal reflection is likely harmless text, not execution.
            is_active = True

            if context == "html":
                if "<" not in payload_str and ">" not in payload_str:
                    is_active = False

            elif context == "attribute":
                # Determine the enclosing quote by scanning backwards
                enclosing_quote = None
                if positions:
                    pos = positions[0]
                    for i in range(pos - 1, -1, -1):
                        if response_text[i] in ['"', "'"]:
                            enclosing_quote = response_text[i]
                            break
                        elif response_text[i] in ['<', '>']:
                            break  # Reached tag boundary

                if not any(c in payload_str for c in ['"', "'", ">", "<"]):
                    if not payload_str.lower().startswith("javascript:"):
                        is_active = False
                    elif enclosing_quote:
                        # javascript: URIs inside quoted attributes are generally safe
                        is_active = False

                if is_active and enclosing_quote and enclosing_quote not in payload_str:
                    is_active = False

            elif context == "javascript":
                if not any(c in payload_str for c in ['"', "'", "<", ">", ";", "}"]):
                    is_active = False
                else:
                    if positions:
                        pos = positions[0]
                        enclosing_quote = None
                        for i in range(pos - 1, -1, -1):
                            if response_text[i] in ['"', "'", "`"]:
                                enclosing_quote = response_text[i]
                                break
                            elif response_text[i] in ['\n', '\r', '<', '>']:
                                break

                        if enclosing_quote and enclosing_quote not in payload_str:
                            if "</script>" not in payload_str.lower():
                                is_active = False

            if is_active:
                result["success"] = True
                result["reason"] = "Payload reflected unescaped and is active in context"
            else:
                result["success"] = False
                result["reason"] = "Payload reflected but appears inactive (safe encoding or text-only)"
        else:
            result["success"] = False
            result["reason"] = "Payload was sanitized, encoded, or not reflected"

        return result

    # Using Max Workers = 5 to be polite but fast
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for p in payloads:
            payload_str = p["payload"]
            if payload_str not in seen_payloads:
                seen_payloads.add(payload_str)
                futures.append(executor.submit(test_payload, p))

        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
                # Early stopping on High confidence success
                if res["success"] and res["confidence"].lower() == "high":
                    executor.shutdown(wait=False, cancel_futures=True)
                    break

    return results
