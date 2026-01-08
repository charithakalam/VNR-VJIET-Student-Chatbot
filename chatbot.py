# chatbot.py
import json
import os
import re
from typing import Any, Dict, List, Optional

class Chatbot:
    def __init__(self, data_path: str = "data/college_details.json"):
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"{data_path} not found. Put college_details.json in data/")
        with open(data_path, "r", encoding="utf-8") as fh:
            self.data: Dict[str, Any] = json.load(fh)

        # common department alias map for HOD lookup
        self.dept_aliases = {
            "cse": "Computer Science & Engineering",
            "computer science": "Computer Science & Engineering",
            "cs": "Computer Science & Engineering",
            "ds": "Artificial Intelligence & Data Science,Cyber Security & Data Science",
            "aids": "Artificial Intelligence & Data Science,Cyber Security & Data Science",
            "cyber": "Artificial Intelligence & Data Science,Cyber Security & Data Science",
            "aiml": "CSE-AI&ML & IoT",
            "it": "Information Technology",
            "ece": "Electronics & Communication Engineering",
            "eee": "Electrical & Electronics Engineering",
            "mech": "Mechanical Engineering",
            "civil": "Civil Engineering",
            "chem": "Chemistry",
            "auto": "Automobile Engineering",
            "eie": "Electronics Instrumentation Engineering",
        }

    # ---------- helpers ----------
    def _normalize(self, s: Optional[str]) -> str:
        if not s:
            return ""
        s2 = re.sub(r"[^\w\s]", " ", s.lower())
        s2 = re.sub(r"\s+", " ", s2).strip()
        return s2

    def _norm_route_token(self, s: str) -> str:
        if not s:
            return ""
        s2 = re.sub(r"[^\w]", "", s).lower()
        # strip leading zeros
        s2 = s2.lstrip("0")
        return s2

    # ---------- HOD ----------
    def get_hod(self, text: str) -> str:
        t = self._normalize(text)
        # check aliases
        for alias, canonical in self.dept_aliases.items():
            if re.search(rf"\b{re.escape(alias)}\b", t):
                return self._format_hod(canonical)

        # check keys in JSON
        hods = self.data.get("hods", {}) or {}
        for key in hods.keys():
            if key.lower() in t:
                return self._format_hod(key)

        return "I couldn't detect the department. Try 'HOD of CSE' or 'HOD of Mechanical'."

    def _format_hod(self, dept_key: str) -> str:
        hods = self.data.get("hods", {}) or {}
        entry = hods.get(dept_key)
        if not entry:
            return f"HOD details for '{dept_key}' are not available."
        name = entry.get("name", "Not listed")
        email = entry.get("email", "Not listed")
        phone = entry.get("phone", "Not listed")
        linkedin = entry.get("linkedin", "") or "Not listed"
        return (f"👩‍🏫 HOD — {dept_key}\n"
                f"Name: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}\n"
                f"LinkedIn: {linkedin}")

    # ---------- Transport: routes ----------
    def get_route(self, text: str) -> str:
        t = self._normalize(text)
        routes = self.data.get("transport", {}).get("routes", []) or []

        # explicit route number match
        m = re.search(r"route\s*([0-9]+[a-zA-Z]?)", t)
        if m:
            token = self._norm_route_token(m.group(1))
            for r in routes:
                rno_norm = self._norm_route_token(str(r.get("route_no", "")))
                if rno_norm == token:
                    out = [
                        f"🚌 Route {r.get('route_no')}",
                        f"From: {r.get('from')}",
                        f"Via: {r.get('via')}",
                        f"Fare: ₹{r.get('fare')}"
                    ]
                    if r.get("timings"):
                        out.append(f"Timings: {r.get('timings')}")
                    return "\n".join(out)
            return f"No route found for '{m.group(1)}'."

        # match by from/via tokens
        tokens = t.split()
        for r in routes:
            from_lower = (r.get("from") or "").lower()
            via_lower = (r.get("via") or "").lower()
            if any(tok in from_lower or tok in via_lower for tok in tokens):
                out = [
                    f"🚌 Route {r.get('route_no')}",
                    f"From: {r.get('from')}",
                    f"Via: {r.get('via')}",
                    f"Fare: ₹{r.get('fare')}"
                ]
                if r.get("timings"):
                    out.append(f"Timings: {r.get('timings')}")
                return "\n".join(out)

        # if user asked "fare" return fare list
        if "fare" in t or "fares" in t:
            lines = ["Route fares:"]
            for r in routes:
                lines.append(f"Route {r.get('route_no')}: ₹{r.get('fare')}")
            return "\n".join(lines)

        # fallback: list available routes
        lines = ["Available routes (route — from → via — fare):"]
        for r in routes:
            lines.append(f"{r.get('route_no')} — {r.get('from')} → {r.get('via')} — ₹{r.get('fare')}")
        return "\n".join(lines)

    # ---------- Transport: drivers ----------
    def get_driver(self, text: str) -> str:
        t = self._normalize(text)
        drivers = self.data.get("drivers", []) or []

        # route-based
        m = re.search(r"route\s*([0-9]+[a-zA-Z]?)", t)
        if m:
            token = self._norm_route_token(m.group(1))
            for d in drivers:
                d_norm = self._norm_route_token(str(d.get("route_no","")))
                if d_norm == token:
                    return f"🧑‍✈️ Driver for route {d.get('route_no')}: {d.get('driver_name')} — {d.get('contact')}"
            return f"No driver found for route '{m.group(1)}'."

        # search by origin or driver name
        for d in drivers:
            if (d.get("from","").lower() in t) or (d.get("driver_name","").lower() in t):
                return f"🧑‍✈️ Driver — {d.get('driver_name')} (Route {d.get('route_no')}, from {d.get('from')}) — {d.get('contact')}"

        # list all drivers
        if "drivers" in t or "driver list" in t or "all drivers" in t:
            lines = ["Drivers (route — name — contact):"]
            for d in drivers:
                lines.append(f"{d.get('route_no')} — {d.get('driver_name')} — {d.get('contact')}")
            return "\n".join(lines)

        return "Please specify the route or origin (e.g., 'driver route 1' or 'driver Patancheru')."

    # ---------- Academics (FIX: strict sem behavior) ----------
    def get_academics(self, text: str) -> str:
        """
        Behavior:
         - If user specifies a semester (sem N), return ONLY events where semester == N.
         - If user specifies a year (1..4) without sem, return all events for that year.
         - If user asks for a specific event type (sessional I/II or End Exams), filter by that event type as well.
         - If the user did NOT include academic-related keywords and no filters were found, return a polite 'no info' message
           instead of the full calendar.
        """
        t = self._normalize(text)
        events = self.data.get("academic_calendar", []) or []

        # If user didn't include academic-related keywords and there are no sem/year/event tokens,
        # avoid returning full calendar to unrelated queries.
        academic_keywords = ["academic", "sessional", "sessional i", "sessional ii",
                             "end exam", "end exams", "semester", "sem", "academic calendar", "sessional1", "sessional2", "ca i", "ca ii"]
        # detect sem first (this is the strict filter)
        sem_m = re.search(r"(?:sem(?:ester)?\s*)([1-8])", t)
        sem_q = sem_m.group(1) if sem_m else None

        # detect year token
        year_map = {
            "1st": "1", "first": "1", "1": "1",
            "2nd": "2", "second": "2", "2": "2",
            "3rd": "3", "third": "3", "3": "3",
            "4th": "4", "fourth": "4", "4": "4"
        }
        year_q = None
        for token, val in year_map.items():
            if re.search(rf"\b{re.escape(token)}\b", t):
                year_q = val
                break

        # detect event type
        event_q = None
        if "sessional i" in t or "sessional 1" in t or re.search(r"\bca[-\s]?i\b", t):
            event_q = "Sessional I"
        elif "sessional ii" in t or "sessional 2" in t or re.search(r"\bca[-\s]?ii\b", t):
            event_q = "Sessional II"
        elif "end exam" in t or "end exams" in t or "semester end" in t or "see" in t:
            event_q = "End Exams"

        # If no sem/year/event tokens AND user didn't explicitly ask about academics, return a friendly prompt instead of full calendar
        if not (sem_q or year_q or event_q) and not any(k in t for k in academic_keywords):
            return "No academic query detected. Try 'sessional I sem 1', 'end exams sem 4', or 'academic calendar 2nd year'."

        matches: List[Dict[str,str]] = []

        # If semester specified -> strict filter by semester (and optional event type)
        if sem_q:
            for ev in events:
                if str(ev.get("semester")) == str(sem_q):
                    if event_q:
                        if event_q.lower() in ev.get("event","").lower():
                            matches.append(ev)
                    else:
                        matches.append(ev)

        # Else if year specified -> filter by year (and optional event type)
        elif year_q:
            for ev in events:
                if str(ev.get("year")) == str(year_q):
                    if event_q:
                        if event_q.lower() in ev.get("event","").lower():
                            matches.append(ev)
                    else:
                        matches.append(ev)

        # Else: try event type only
        else:
            if event_q:
                for ev in events:
                    if event_q.lower() in ev.get("event","").lower():
                        matches.append(ev)

        if not matches:
            # helpful hint message
            if sem_q:
                return f"No academic events found for semester {sem_q} with that filter."
            if year_q:
                return f"No academic events found for year {year_q} with that filter."
            return "No academic events found. Try 'sessional I sem 1', 'end exams sem 4', or 'academic calendar 2nd year'."

        # group by Year-Semester
        grouped: Dict[str, List[Dict[str,str]]] = {}
        for ev in matches:
            key = f"Year {ev.get('year')} — Semester {ev.get('semester')}"
            grouped.setdefault(key, []).append(ev)

        lines: List[str] = []
        # keep keys sorted by year then semester numerically for nicer display
        def sort_key(k: str):
            m = re.search(r"Year\s+(\d+)\s+—\s+Semester\s+(\d+)", k)
            if m:
                return (int(m.group(1)), int(m.group(2)))
            return (99,99)
        for key in sorted(grouped.keys(), key=sort_key):
            lines.append(f"📘 {key}")
            for ev in grouped[key]:
                lines.append(f"• {ev.get('event')}: {ev.get('dates')}")
        return "\n".join(lines)


    # ---------- General info ----------
    def get_contact(self) -> str:
        d = self.data
        phones = d.get("phone", []) or []
        phone_txt = ", ".join(phones) if isinstance(phones, list) else str(phones)
        return (f"🏫 {d.get('name')}\n"
                f"📍 Address: {d.get('address')}\n"
                f"📧 Email: {d.get('email')}\n"
                f"📞 Phone: {phone_txt}\n"
                f"🔗 Website: {d.get('website')}")

    def get_about(self) -> str:
        return f"ℹ️ {self.data.get('about','No about info available.')}"

    def get_facilities(self) -> str:
        fac = self.data.get("facilities", []) or []
        if not fac:
            return "No facilities listed."
        return "🏢 Campus facilities:\n" + "\n".join(f"• {x}" for x in fac)

    # ---------- Dispatcher ----------
    def answer(self, text: str) -> str:
        t = self._normalize(text)
        if not t:
            return "Please ask something like 'HOD of CSE', 'route 2', 'driver route 1', or 'sessional I sem 1'."

        # HOD
        if any(w in t for w in ["hod", "head of", "who is hod", "who is head"]):
            return self.get_hod(text)

        # driver
        if "driver" in t or "drivers" in t or "driver list" in t:
            return self.get_driver(text)

        # transport routes or fares
        if any(w in t for w in ["route", "routes", "bus", "transport", "fare", "fares"]):
            return self.get_route(text)

        # academics
        if any(w in t for w in ["academic", "sessional", "sessional i", "sessional ii", "end exam", "end exams", "sem", "semester"]):
            return self.get_academics(text)

        # contact/address
        if any(w in t for w in ["address", "contact", "email", "phone", "where is"]):
            return self.get_contact()

        # facilities/about
        if any(w in t for w in ["facility", "facilities", "amenities"]):
            return self.get_facilities()
        if any(w in t for w in ["about", "vnr", "vnrvjiet", "vjiet"]):
            return self.get_about()

        # fallback (best-effort)
        # prefer hod -> driver -> route -> academic
                # fallback (best-effort)
                # fallback (best-effort)

        # Try HOD first
        r = self.get_hod(text)
        if "couldn't detect" not in r and "not available" not in r:
            return r

        # Try driver next
        r = self.get_driver(text)
        if "Please specify" not in r and "No driver found" not in r:
            return r

        # Only consider routes if the query looks transport-related
        if any(w in t for w in ["route", "routes", "bus", "transport", "fare", "fares"]):
            r = self.get_route(text)
            # get_route returns a route list for no-match; consider it a match ONLY if the text contained transport keywords
            if "No route" not in r:
                return r

        # Do NOT call get_academics() here unconditionally — it may return the full calendar.
        # Academics are handled earlier in the dispatcher when the user includes academic keywords.

        # Final fallback
        return "Cannot find information related to that query."

# ---------------- Quick manual test ----------------
if __name__ == "__main__":
    bot = Chatbot("data/college_details.json")
    tests = [
        "end exams of sem 4",
        "end exams sem 3",
        "sessional I sem 1",
        "academic calendar 2nd year",
        "route 2",
        "driver route 2",
        "HOD of CSE"
    ]
    for q in tests:
        print("Q:", q)
        print(bot.answer(q))
        print("-" * 60)
