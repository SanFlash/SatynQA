"""
PlaywrightAI — Automation CheatSheet Generator
Render deployment: gunicorn app:app
Local:            python app.py  →  http://localhost:5000
"""

import os, io
from flask import Flask, request, jsonify, send_file, Response

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  AUTOMATION TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────

TEMPLATES = {

# ── LOGIN ─────────────────────────────────────────────────────────────────────
"login": {
"title": "Login Form Automation",
"category": "Authentication",
"use_case": (
    "Automates the complete login flow: navigates to the login page, fills in "
    "username and password, clicks submit, and verifies the successful redirect "
    "to the dashboard. Essential for smoke tests and CI/CD pipelines."
),
"html_example": """\
<form action="/login" method="POST">
  <input type="text"     id="username" placeholder="Username" />
  <input type="password" id="password" placeholder="Password" />
  <button type="submit" class="btn btn-primary">Login</button>
</form>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to login page
        page.goto("https://practicetestautomation.com/practice-test-login/")
        page.wait_for_load_state("networkidle")

        # Fill credentials
        page.fill("#username", "student")
        page.fill("#password", "Password123")

        # Submit the form
        page.click("button[class='btn btn-primary']")

        # Wait for successful redirect
        page.wait_for_url("**/logged-in-successfully/**", timeout=10000)

        # Assert login success
        expect(page.locator("h1")).to_contain_text("Logged In Successfully")
        print("✅ Login successful!")

        browser.close()

run()
""",
"steps": [
    ("Launch Browser", "p.chromium.launch(headless=False) opens a visible Chrome window"),
    ("Navigate", "page.goto(url) then wait_for_load_state('networkidle') ensures full load"),
    ("Fill Username", "page.fill('#username', 'student') types into the username field"),
    ("Fill Password", "page.fill('#password', 'Password123') types into the password field"),
    ("Submit", "page.click('button[class=...]') clicks the login submit button"),
    ("Wait for Redirect", "page.wait_for_url('**/logged-in**') waits for dashboard URL"),
    ("Assert Success", "expect(page.locator('h1')).to_contain_text('Logged In') verifies login"),
],
"edge_cases": [
    ("Wrong Credentials", "Assert error element: expect(page.locator('.error')).to_be_visible()"),
    ("Network Timeout", "Increase timeout: page.goto(url, timeout=30000) and catch TimeoutError"),
    ("Remember Me", "Tick checkbox before submit: page.check('#remember-me')"),
    ("2FA / OTP Field", "page.wait_for_selector('#otp-input') then fill OTP after login step"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright, expect
from playwright.sync_api import TimeoutError as PWTimeout

def login_with_retry(url, username, password, max_retries=3):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for attempt in range(1, max_retries + 1):
            try:
                print(f"Attempt {attempt}/{max_retries}...")
                page.goto(url, wait_until="networkidle", timeout=15000)

                # Locator API — more robust than fill()
                page.locator("#username").fill(username)
                page.locator("#password").fill(password)
                page.locator("button[type='submit']").click()

                page.wait_for_url("**/logged-in**", timeout=8000)
                expect(page.locator("h1")).to_contain_text("Logged In")
                print(f"✅ Login OK on attempt {attempt}")
                break

            except PWTimeout:
                print(f"⚠️  Timed out on attempt {attempt}. Retrying...")
                page.reload()
            except Exception as e:
                print(f"❌ Error: {e}")
                page.screenshot(path=f"login_fail_{attempt}.png")
                if attempt == max_retries:
                    raise

        browser.close()

login_with_retry(
    "https://practicetestautomation.com/practice-test-login/",
    "student",
    "Password123"
)
""",
"expected_behavior": [
    "Browser opens — Chrome window appears on screen",
    "Login page loads — username and password fields are visible",
    "Credentials typed into fields automatically",
    "Submit button clicked — POST request fires to server",
    "Browser redirects to the dashboard / success URL",
    "Heading text verified — test passes with confirmation print",
],
},

# ── SIGNUP ─────────────────────────────────────────────────────────────────────
"signup": {
"title": "Signup / Registration Form Automation",
"category": "Authentication",
"use_case": (
    "Automates new user registration: fills all form fields with unique test data, "
    "accepts terms checkbox, submits, and verifies the account creation confirmation. "
    "Uses UUID to prevent duplicate username errors across runs."
),
"html_example": """\
<form id="signup-form">
  <input type="text"     id="firstName"  placeholder="First Name" />
  <input type="text"     id="lastName"   placeholder="Last Name" />
  <input type="text"     id="userName"   placeholder="Username" />
  <input type="password" id="password"   placeholder="Password" />
  <input type="checkbox" id="terms" />
  <label for="terms">I agree to Terms</label>
  <button id="register">Register</button>
</form>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright, expect
import uuid

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://demoqa.com/register")
        page.wait_for_load_state("domcontentloaded")

        # Unique username to avoid conflicts between runs
        unique = uuid.uuid4().hex[:6]

        page.fill("#firstName", "Test")
        page.fill("#lastName",  "User")
        page.fill("#userName",  f"user_{unique}")
        page.fill("#password",  "Test@1234!")

        # Scroll register button into view and click
        page.locator("#register").scroll_into_view_if_needed()
        page.click("#register")

        # Verify success output
        page.wait_for_selector("#output", timeout=8000)
        output_text = page.locator("#output").inner_text()
        print(f"✅ Registration result: {output_text}")
        assert len(output_text) > 0

        browser.close()

run()
""",
"steps": [
    ("Navigate", "Open registration page, wait for domcontentloaded"),
    ("Unique Data", "uuid.uuid4().hex[:6] generates a unique username every run"),
    ("Fill Fields", "page.fill('#firstName', value) for each input field"),
    ("Scroll & Submit", "scroll_into_view_if_needed() ensures button is visible before click"),
    ("Verify", "Read #output inner_text() and assert it confirms registration"),
],
"edge_cases": [
    ("Duplicate Username", "Generate unique name with uuid; catch and assert error element"),
    ("Weak Password", "Match site rules — include upper, lower, digit, special character"),
    ("Required Field Skip", "Submit empty form and assert each required field shows error"),
    ("Slow Network", "Increase wait_for_selector timeout to 15000ms on slow connections"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright
import uuid, time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # Record video of the entire test
        context = browser.new_context(record_video_dir="videos/")
        page = context.new_page()

        unique = uuid.uuid4().hex[:6]

        fields = {
            "firstName": "Jane",
            "lastName":  "Tester",
            "userName":  f"user_{unique}",
            "password":  "Secure@Pass1"
        }

        try:
            page.goto("https://demoqa.com/register")
            for field_id, value in fields.items():
                page.locator(f"#{field_id}").fill(value)
                page.wait_for_timeout(80)  # human-like typing pace

            page.screenshot(path=f"before_register_{unique}.png")
            page.locator("#register").click()
            page.wait_for_selector("#output", timeout=8000)

            result = page.locator("#output").inner_text()
            print(f"✅ Registration: {result}")
            page.screenshot(path=f"after_register_{unique}.png")

        finally:
            context.close()
            browser.close()

run()
""",
"expected_behavior": [
    "Browser opens the registration page",
    "All fields filled with unique test data automatically",
    "Register button scrolled into view and clicked",
    "Success output text appears confirming registration",
    "Screenshots saved before and after — video recorded",
],
},

# ── CLICK ─────────────────────────────────────────────────────────────────────
"click": {
"title": "Button Click & Dialog Handling",
"category": "User Interactions",
"use_case": (
    "Automates single click, double click, and right-click actions. "
    "Handles JS alert/confirm dialogs, confirmation modals, and dynamic DOM "
    "changes triggered after button click events."
),
"html_example": """\
<button id="alertButton">Show Alert</button>
<button id="confirmButton">Show Confirm</button>
<button id="doubleClickBtn">Double Click Me</button>
<button id="rightClickBtn">Right Click Me</button>
<div id="doubleClickMessage"></div>
<div id="rightClickMessage"></div>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # ── JS Alert ──────────────────────────────
        page.goto("https://demoqa.com/alerts")
        page.wait_for_load_state("domcontentloaded")

        page.on("dialog", lambda dialog: dialog.accept())
        page.click("#alertButton")
        page.wait_for_timeout(500)
        print("✅ Alert accepted!")

        # ── Confirm Dialog ─────────────────────────
        def handle_confirm(dialog):
            print(f"Confirm text: {dialog.message}")
            dialog.accept()

        page.on("dialog", handle_confirm)
        page.click("#confirmButton")
        page.wait_for_timeout(500)
        print("✅ Confirm accepted!")

        # ── Double Click ───────────────────────────
        page.goto("https://demoqa.com/buttons")
        page.wait_for_load_state("domcontentloaded")
        page.dblclick("#doubleClickBtn")
        expect(page.locator("#doubleClickMessage")).to_have_text(
            "You have done a double click"
        )
        print("✅ Double click confirmed!")

        # ── Right Click ────────────────────────────
        page.click("#rightClickBtn", button="right")
        expect(page.locator("#rightClickMessage")).to_have_text(
            "You have done a right click"
        )
        print("✅ Right click confirmed!")

        browser.close()

run()
""",
"steps": [
    ("Navigate", "Go to page and wait for domcontentloaded"),
    ("Dialog Handler", "page.on('dialog', lambda d: d.accept()) auto-handles alerts"),
    ("Single Click", "page.click('#btn') — fires click event"),
    ("Double Click", "page.dblclick('#btn') — fires dblclick event"),
    ("Right Click", "page.click('#btn', button='right') — opens context menu"),
    ("Assert Message", "expect(locator).to_have_text('expected') verifies result"),
],
"edge_cases": [
    ("Disabled Button", "expect(locator).to_be_enabled(timeout=5000) before clicking"),
    ("Prompt Dialog", "dialog.fill('my input') before dialog.accept() for prompt()"),
    ("Click Outside Modal", "page.click('body', position={'x':5,'y':5}) to dismiss"),
    ("Timer Alert", "page.wait_for_selector triggers after N seconds automatically"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Intercept all dialogs and log them
        dialog_log = []
        def on_dialog(dialog):
            dialog_log.append({"type": dialog.type, "msg": dialog.message})
            dialog.accept()

        page.on("dialog", on_dialog)

        page.goto("https://demoqa.com/alerts")
        page.wait_for_load_state("domcontentloaded")

        # Click all alert types
        for btn_id in ["alertButton", "confirmButton", "promtButton"]:
            try:
                page.click(f"#{btn_id}")
                page.wait_for_timeout(600)
            except Exception as e:
                print(f"  Skipped #{btn_id}: {e}")

        print(f"Dialogs handled: {dialog_log}")

        # Dynamic button — wait until enabled
        page.goto("https://demoqa.com/dynamic-properties")
        btn = page.locator("#enableAfter")
        expect(btn).to_be_enabled(timeout=8000)
        btn.click()
        print("✅ Dynamic button clicked after it became enabled!")

        browser.close()

run()
""",
"expected_behavior": [
    "Browser opens and loads the alerts page",
    "JS alert fires — dialog handler accepts it automatically",
    "Confirm dialog message is logged, then accepted",
    "Double-click on button triggers success message",
    "Right-click triggers right-click confirmation message",
],
},

# ── IFRAME ─────────────────────────────────────────────────────────────────────
"iframe": {
"title": "iFrame Content Handling",
"category": "Advanced Elements",
"use_case": (
    "Automates interactions inside embedded iFrames such as rich text editors, "
    "payment widgets, and third-party forms. Uses Playwright's frame_locator API "
    "to switch context without any extra browser flags."
),
"html_example": """\
<iframe id="mce_0_ifr"
  src="javascript:;"
  title="Rich Text Area. Press ALT-F9 for menu.">
  <body id="tinymce" class="mce-content-body">
    <p>Your content here...</p>
  </body>
</iframe>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Page with embedded TinyMCE iFrame
        page.goto("https://the-internet.herokuapp.com/iframe")
        page.wait_for_load_state("networkidle")

        # Wait for iframe to attach
        page.wait_for_selector("#mce_0_ifr", state="attached", timeout=10000)

        # Switch context into the iframe using frame_locator
        frame = page.frame_locator("#mce_0_ifr")

        # Wait for editor inside the frame
        editor = frame.locator("#tinymce")
        editor.wait_for(state="visible", timeout=10000)

        # Clear and type inside the iframe
        editor.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        editor.type("Playwright automation inside iFrame!", delay=50)

        # Read and verify the content
        content = editor.inner_text()
        assert "Playwright automation" in content
        print(f"✅ iFrame content: {content}")

        page.screenshot(path="iframe_done.png")
        browser.close()

run()
""",
"steps": [
    ("Navigate", "Go to page with iframe, wait for networkidle"),
    ("Wait Attached", "page.wait_for_selector('#mce_0_ifr', state='attached') ensures iframe loaded"),
    ("frame_locator", "page.frame_locator('#mce_0_ifr') switches DOM context into the frame"),
    ("Wait Inside", "frame.locator('#tinymce').wait_for(state='visible') before acting"),
    ("Type Inside", "editor.click() then editor.type() — all scoped inside frame"),
    ("Verify", "editor.inner_text() reads content — assert expected text present"),
],
"edge_cases": [
    ("Nested iFrames", "Chain: page.frame_locator('#outer').frame_locator('#inner-frame')"),
    ("Dynamic src", "Use title: page.frame_locator('iframe[title=\"Rich Text Area\"]')"),
    ("Cross-Origin", "Playwright handles cross-origin iframes natively — no special flags"),
    ("Frame Not Ready", "frame.locator('#el').wait_for(state='visible', timeout=10000)"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://the-internet.herokuapp.com/iframe")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("#mce_0_ifr", state="attached", timeout=10000)

        frame = page.frame_locator("#mce_0_ifr")
        editor = frame.locator("#tinymce")
        editor.wait_for(state="visible", timeout=10000)

        # Select all and replace
        editor.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Delete")
        editor.type("Hello from Playwright iFrame test!", delay=60)

        # Also interact with main page elements
        page.locator("h3").first.scroll_into_view_if_needed()

        content = editor.inner_text()
        print(f"✅ Editor content: {content}")
        assert "Hello from Playwright" in content

        page.screenshot(path="iframe_advanced.png")
        browser.close()

run()
""",
"expected_behavior": [
    "Page loads with embedded TinyMCE iFrame",
    "Playwright waits for iframe to attach to DOM",
    "Context switches inside frame using frame_locator",
    "Existing text cleared — new text typed inside editor",
    "Content verified programmatically — screenshot captured",
],
},

# ── SCROLL ─────────────────────────────────────────────────────────────────────
"scroll": {
"title": "Infinite Scroll Automation",
"category": "Scrolling",
"use_case": (
    "Automates all scrolling patterns: scroll to bottom, infinite scroll feeds, "
    "and scroll to a specific element. Detects end-of-content by comparing "
    "page height before and after each scroll."
),
"html_example": """\
<div id="feed" class="infinite-feed">
  <article class="post-card">Post 1</article>
  <article class="post-card">Post 2</article>
  <!-- More articles load automatically as user scrolls -->
</div>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://infinite-scroll.com/demo/full-page/")
        page.wait_for_load_state("networkidle")

        max_scrolls = 5
        last_height = 0

        for i in range(max_scrolls):
            # Scroll to bottom of page
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)  # wait for new content to load

            new_height = page.evaluate("document.body.scrollHeight")
            print(f"Scroll {i+1}: height = {new_height}px")

            if new_height == last_height:
                print("✅ Reached end of page — no more content!")
                break

            last_height = new_height

        # Scroll back to top
        page.evaluate("window.scrollTo(0, 0)")
        print("Done!")
        browser.close()

run()
""",
"steps": [
    ("Navigate", "Open page and wait for initial content to load"),
    ("Record Height", "page.evaluate('document.body.scrollHeight') gets current height"),
    ("Scroll Down", "page.evaluate('window.scrollTo(0, document.body.scrollHeight)')"),
    ("Wait for Load", "page.wait_for_timeout(2000) — new items need time to render"),
    ("Compare Heights", "If height unchanged after scroll — end of content reached"),
    ("Scroll to Element", "locator.scroll_into_view_if_needed() for specific target"),
],
"edge_cases": [
    ("Lazy Load Before Bottom", "Scroll in steps: page.evaluate('window.scrollBy(0, 800)')"),
    ("Loading Spinner", "page.wait_for_selector('.spinner', state='hidden') before counting"),
    ("Scroll to Element", "page.locator('#target-element').scroll_into_view_if_needed()"),
    ("Horizontal Scroll", "page.evaluate('document.querySelector(\"#el\").scrollLeft += 400')"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright

def scroll_and_collect(url, item_selector, max_scrolls=8):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")

        collected = set()
        prev_count = 0

        for scroll_num in range(1, max_scrolls + 1):
            # Collect all visible items
            for el in page.locator(item_selector).all():
                try:
                    collected.add(el.inner_text().strip())
                except Exception:
                    pass

            print(f"Scroll {scroll_num}: {len(collected)} unique items")

            # Scroll in 3 incremental steps for reliability
            for _ in range(3):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                page.wait_for_timeout(600)

            # Wait out any loading spinner
            try:
                page.wait_for_selector(".loader", state="hidden", timeout=3000)
            except Exception:
                pass

            if len(collected) == prev_count:
                print("✅ No new items — end of feed!")
                break

            prev_count = len(collected)

        browser.close()
        return list(collected)

items = scroll_and_collect(
    "https://infinite-scroll.com/demo/full-page/",
    "article",
    max_scrolls=5
)
print(f"Collected {len(items)} items total.")
""",
"expected_behavior": [
    "Page opens and initial articles render",
    "Script scrolls to bottom — new articles load",
    "Page height increases each scroll iteration",
    "When height stops growing — end of feed detected and loop exits",
    "All collected item text is returned for processing",
],
},

# ── DROPDOWN ──────────────────────────────────────────────────────────────────
"dropdown": {
"title": "Dropdown & Select Handling",
"category": "Form Handling",
"use_case": (
    "Automates native HTML select elements and custom CSS/React dropdowns. "
    "Handles select-by-label, select-by-value, multi-select, "
    "and searchable autocomplete dropdowns."
),
"html_example": """\
<!-- Native HTML select -->
<select id="oldSelectMenu">
  <option value="1">Yellow</option>
  <option value="2">Blue</option>
  <option value="3">Red</option>
</select>

<!-- Multi-select -->
<select id="cars" multiple>
  <option value="volvo">Volvo</option>
  <option value="saab">Saab</option>
</select>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://demoqa.com/select-menu")
        page.wait_for_load_state("domcontentloaded")

        # ── Native <select> — by label ─────────────
        page.select_option("#oldSelectMenu", label="Yellow")
        print("✅ Native select: Yellow chosen")

        # ── Native <select> — by value ─────────────
        # page.select_option("#oldSelectMenu", value="2")

        # ── Multi-select ───────────────────────────
        page.select_option("#cars", ["volvo", "saab"])
        selected = page.eval_on_selector_all(
            "#cars option:checked",
            "els => els.map(e => e.textContent)"
        )
        print(f"✅ Multi-select: {selected}")

        # ── Custom React dropdown ──────────────────
        page.click("#react-select-3-input")
        page.wait_for_timeout(300)
        page.fill("#react-select-3-input", "Dr")
        page.wait_for_selector(".react-select__option", state="visible")
        page.locator(".react-select__option").first.click()
        print("✅ React dropdown selected!")

        browser.close()

run()
""",
"steps": [
    ("Navigate", "Open form page, wait for domcontentloaded"),
    ("Native Select by Label", "page.select_option('#id', label='Yellow') — uses visible text"),
    ("Select by Value", "page.select_option('#id', value='2') — uses value attribute"),
    ("Multi-Select", "page.select_option('#cars', ['volvo', 'saab']) — pass a list"),
    ("Custom Dropdown", "Click trigger → type search → wait for options → click match"),
    ("Verify", "page.eval_on_selector_all('#id option:checked', ...) reads all selected"),
],
"edge_cases": [
    ("Select by Index", "page.select_option('#el', index=2) — selects by position"),
    ("Disabled Option", "Check: page.locator('option[value=X]').get_attribute('disabled')"),
    ("Dependent Dropdowns", "After first selection, wait for second dropdown to repopulate"),
    ("Searchable Dropdown", "Fill hidden search input inside custom dropdown, pick result"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://demoqa.com/select-menu")
        page.wait_for_load_state("domcontentloaded")

        # Select with immediate verification
        page.select_option("#oldSelectMenu", label="Yellow")
        selected = page.eval_on_selector(
            "#oldSelectMenu option:checked",
            "el => el.textContent"
        )
        assert selected.strip() == "Yellow"
        print(f"✅ Verified: {selected.strip()}")

        # Multi-select with verification
        page.select_option("#cars", ["volvo", "saab", "opel"])
        selected_values = page.eval_on_selector_all(
            "#cars option:checked",
            "els => els.map(e => e.textContent)"
        )
        print(f"✅ Multi-selected: {selected_values}")

        # Searchable React dropdown with typed input
        inp = page.locator("#react-select-4-input")
        inp.click()
        inp.type("Dr", delay=80)
        page.wait_for_selector(".react-select__option")
        options = page.locator(".react-select__option").all()
        print(f"Found {len(options)} options matching 'Dr'")
        options[0].click()

        browser.close()

run()
""",
"expected_behavior": [
    "Page loads with select elements visible",
    "Native select changes to Yellow — verified by option:checked",
    "Multi-select holds two values simultaneously",
    "Custom dropdown opens on click — search filters options",
    "First matching option is clicked — dropdown closes",
],
},

# ── HOVER ─────────────────────────────────────────────────────────────────────
"hover": {
"title": "Hover Menu Navigation",
"category": "User Interactions",
"use_case": (
    "Automates hover-triggered navigation menus, tooltips, and flyout panels. "
    "Uses hover() and precise bounding_box mouse moves for sticky animated menus."
),
"html_example": """\
<nav id="nav">
  <ul>
    <li><a href="#">Main Item 1</a></li>
    <li>
      <a href="#">Main Item 2</a>
      <ul class="submenu">
        <li><a href="#">SUB SUB LIST »</a>
          <ul>
            <li><a href="#">Sub Sub Item 1</a></li>
          </ul>
        </li>
      </ul>
    </li>
  </ul>
</nav>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://demoqa.com/menu")
        page.wait_for_load_state("domcontentloaded")

        # Hover over main menu item
        page.hover("#nav a:has-text('Main Item 2')")
        page.wait_for_timeout(400)

        # Hover to reveal deeper submenu
        page.hover("text=SUB SUB LIST")
        page.wait_for_timeout(300)

        # Click the final sub-item
        page.click("text=Sub Sub Item 1")
        page.wait_for_timeout(400)
        print("✅ Hover navigation complete!")

        # ── Tooltip verification ───────────────────
        page.goto("https://demoqa.com/tool-tips")
        page.hover("#toolTipButton")
        page.wait_for_selector(".tooltip-inner", state="visible")
        tip = page.locator(".tooltip-inner").inner_text()
        print(f"✅ Tooltip text: {tip}")

        browser.close()

run()
""",
"steps": [
    ("Navigate", "Open page with hover navigation menu"),
    ("Hover Parent", "page.hover('#menu-item') fires mouseover — submenu appears"),
    ("Wait for CSS", "page.wait_for_timeout(400) lets CSS transition complete"),
    ("Hover Sub-item", "page.hover('text=SUB SUB LIST') reveals deeper nesting"),
    ("Click Target", "page.click('text=Sub Sub Item 1') navigates to target"),
    ("Tooltip", "hover() → wait_for_selector('.tooltip-inner', state='visible')"),
],
"edge_cases": [
    ("CSS Transition Delay", "Add wait_for_timeout(300) after hover for animated menus"),
    ("Hover Leaves Focus", "Use mouse.move() with steps=10 for sticky/slow menus"),
    ("Mobile Menu", "Mobile shows hamburger — check viewport width first"),
    ("Tooltip Stuck Open", "page.mouse.move(0, 0) to move away and dismiss tooltip"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://demoqa.com/menu")
        page.wait_for_load_state("domcontentloaded")

        # Slow precise mouse movement — works on sticky menus
        trigger = page.locator("text=Main Item 2")
        box = trigger.bounding_box()
        page.mouse.move(
            box["x"] + box["width"] / 2,
            box["y"] + box["height"] / 2,
            steps=10
        )
        page.wait_for_timeout(400)

        sub = page.locator("text=SUB SUB LIST")
        sub_box = sub.bounding_box()
        page.mouse.move(
            sub_box["x"] + sub_box["width"] / 2,
            sub_box["y"] + sub_box["height"] / 2,
            steps=8
        )
        page.wait_for_timeout(300)

        page.locator("text=Sub Sub Item 1").click()
        print(f"✅ Navigated via hover to: {page.url}")
        browser.close()

run()
""",
"expected_behavior": [
    "Browser opens the menu page",
    "Mouse hovers over Main Item 2 — submenu slides out",
    "Mouse moves to SUB SUB LIST — nested submenu opens",
    "Sub Sub Item 1 clicked — page interaction recorded",
    "URL or page state confirms successful navigation",
],
},

# ── WAITS ─────────────────────────────────────────────────────────────────────
"waits": {
"title": "Waits & Synchronisation",
"category": "Waits & Sync",
"use_case": (
    "Replaces time.sleep() with smart Playwright waits. Covers element visibility, "
    "network idle, custom JS conditions, API response interception, "
    "and global timeout configuration."
),
"html_example": """\
<!-- Element that enables after 5 seconds -->
<button id="enableAfter" disabled>Will Enable</button>

<!-- Element that appears after delay -->
<div id="visibleAfter" class="hidden">Now Visible!</div>

<!-- Element that changes colour -->
<button id="colorChange">Changes Color</button>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Global default timeouts
        page.set_default_timeout(15000)
        page.set_default_navigation_timeout(30000)

        # ── Wait for network idle ──────────────────
        page.goto(
            "https://demoqa.com/dynamic-properties",
            wait_until="networkidle"
        )

        # ── Wait for element to appear ─────────────
        page.wait_for_selector("#visibleAfter", state="visible", timeout=8000)
        expect(page.locator("#visibleAfter")).to_be_visible()
        print("✅ Element appeared!")

        # ── Wait for element to become enabled ─────
        page.wait_for_selector(
            "#enableAfter:not([disabled])", timeout=8000
        )
        expect(page.locator("#enableAfter")).to_be_enabled()
        page.click("#enableAfter")
        print("✅ Clicked after element became enabled!")

        # ── Custom JS condition ────────────────────
        page.wait_for_function(
            "document.querySelector('#colorChange') !== null"
        )
        print("✅ JS condition satisfied!")

        browser.close()

run()
""",
"steps": [
    ("Global Timeouts", "page.set_default_timeout(15000) applies to all wait calls"),
    ("networkidle", "page.goto(url, wait_until='networkidle') — no pending XHR"),
    ("wait_for_selector", "page.wait_for_selector('#el', state='visible', timeout=8000)"),
    ("wait_for_function", "page.wait_for_function('JS expression') for custom conditions"),
    ("expect assertions", "expect(locator).to_be_enabled() auto-retries until timeout"),
    ("Intercept API", "page.expect_response('**/api/**') waits for specific network call"),
],
"edge_cases": [
    ("SPA Navigation", "Use wait_for_url() not wait_for_load_state for React/Vue apps"),
    ("Flaky Element", "expect(locator).to_be_visible(timeout=15000) auto-retries"),
    ("Race Condition", "Use wait_for_load_state('networkidle') after every click in SPA"),
    ("Timeout Too Short", "Increase per-call: wait_for_selector('#el', timeout=30000)"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(15000)

        # Intercept API response while clicking refresh
        page.goto("https://demoqa.com/books")

        with page.expect_response(
            lambda r: "BookStore" in r.url and r.status == 200
        ) as resp_info:
            page.reload()

        response = resp_info.value
        print(f"✅ API: {response.url} → HTTP {response.status}")

        # Wait for CSS colour change (dynamic property test)
        page.goto("https://demoqa.com/dynamic-properties")
        page.wait_for_function(
            "getComputedStyle(document.getElementById('colorChange')).color "
            "=== 'rgb(220, 53, 69)'"
        )
        print("✅ Color changed to red!")

        # Wait for button that enables after 5s
        expect(
            page.locator("#enableAfter")
        ).to_be_enabled(timeout=8000)
        page.locator("#enableAfter").click()
        print("✅ Enabled button clicked!")

        browser.close()

run()
""",
"expected_behavior": [
    "Navigation waits for all XHR requests to complete",
    "Dynamic element visibility detected without hard sleep",
    "Custom JS condition evaluates — triggers when satisfied",
    "Button enables after delay — clicked exactly when ready",
    "API response intercepted — status code confirmed",
],
},

# ── UPLOAD ─────────────────────────────────────────────────────────────────────
"upload": {
"title": "File Upload Automation",
"category": "Form Handling",
"use_case": (
    "Uploads files without triggering the OS file picker dialog. "
    "Works on standard inputs, hidden inputs, and handles the download flow. "
    "Uses set_input_files for a clean, cross-platform approach."
),
"html_example": """\
<input type="file" id="uploadFile" accept=".txt,.pdf,.png" />
<div id="uploadedFilePath">No file chosen</div>
<a id="downloadButton" href="/download/sampleFile.jpeg">Download</a>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright, expect
import os, tempfile

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://demoqa.com/upload-download")
        page.wait_for_load_state("domcontentloaded")

        # Create a real temp file to upload
        tmp = tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w"
        )
        tmp.write("Hello from Playwright automation test!")
        tmp.close()

        # Upload — no OS dialog triggered
        page.set_input_files("#uploadFile", tmp.name)

        # Verify filename shown on page
        shown = page.locator("#uploadedFilePath").inner_text()
        assert os.path.basename(tmp.name) in shown
        print(f"✅ Uploaded: {shown}")

        # Cleanup temp file
        os.unlink(tmp.name)

        # ── Download flow ──────────────────────────
        with page.expect_download() as dl_info:
            page.click("#downloadButton")

        dl = dl_info.value
        dl.save_as("downloaded_sample.jpeg")
        print(f"✅ Downloaded: {dl.suggested_filename}")

        browser.close()

run()
""",
"steps": [
    ("Create File", "tempfile.NamedTemporaryFile() creates a real file — no manual prep"),
    ("set_input_files", "page.set_input_files('#uploadFile', path) — bypasses OS dialog"),
    ("Verify Display", "Read #uploadedFilePath text, assert it contains the filename"),
    ("Cleanup", "os.unlink(tmp.name) removes the temp file after upload"),
    ("Download", "page.expect_download() context manager, then .save_as(path)"),
],
"edge_cases": [
    ("Hidden Input", "set_input_files works on display:none inputs — bypasses visibility"),
    ("Multiple Files", "page.set_input_files('#input', ['file1.pdf', 'file2.png'])"),
    ("File Too Large", "Upload oversized file and assert error validation message"),
    ("Wrong Format", "Upload wrong extension and assert validation error appears"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright
import os, tempfile

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://demoqa.com/upload-download")

        # Log all network requests
        def log_req(req):
            if "upload" in req.url.lower() or "download" in req.url.lower():
                print(f"  Network: {req.method} {req.url}")

        page.on("request", log_req)

        # Create and upload multiple test files
        files = []
        for i in range(2):
            f = tempfile.NamedTemporaryFile(
                suffix=f"_test{i}.txt", delete=False, mode="w"
            )
            f.write(f"Test file {i} content from Playwright")
            f.close()
            files.append(f.name)

        page.set_input_files("#uploadFile", files[0])  # upload first
        shown = page.locator("#uploadedFilePath").inner_text()
        print(f"✅ Upload confirmed: {shown}")

        # Download
        with page.expect_download() as dl:
            page.click("#downloadButton")

        download = dl.value
        save_path = "playwright_download.jpeg"
        download.save_as(save_path)
        print(f"✅ Saved to: {os.path.abspath(save_path)}")

        for f in files:
            os.unlink(f)

        browser.close()

run()
""",
"expected_behavior": [
    "Temp test file created automatically — no manual setup needed",
    "set_input_files attaches file without OS dialog appearing",
    "Filename shown in the page UI — verified programmatically",
    "Download button clicked — file saved to local disk",
    "Absolute path of downloaded file printed to confirm",
],
},

# ── ERRORS ─────────────────────────────────────────────────────────────────────
"errors": {
"title": "Error Handling & Retry Logic",
"category": "Error Handling",
"use_case": (
    "Builds resilient automation with try/except blocks, automatic retries, "
    "screenshot-on-failure, console error capture, and network request logging. "
    "Essential for CI/CD pipelines where flakiness must be handled gracefully."
),
"html_example": """\
<button id="enableAfter" disabled>Enabled After 5s</button>
<button id="visibleAfter" style="display:none">Appears After 5s</button>
<div class="error-banner hidden">Request failed. Try again.</div>""",
"playwright_code": """\
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PWTimeout
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Capture JS console errors and page errors
        console_errors = []
        page.on("console",   lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: console_errors.append(str(e)))

        try:
            page.goto("https://demoqa.com/dynamic-properties", timeout=15000)
            page.wait_for_load_state("networkidle")

            # Wait for element that appears after delay
            page.wait_for_selector("#visibleAfter", state="visible", timeout=8000)
            page.click("#visibleAfter")
            print("✅ Clicked dynamic element!")

        except PWTimeout as e:
            print(f"❌ Timeout: {e}")
            page.screenshot(path="timeout_error.png")

        except Exception as e:
            print(f"❌ Error: {e}")
            page.screenshot(path="general_error.png")

        finally:
            if console_errors:
                print(f"Console errors captured: {console_errors}")
            browser.close()

run()
""",
"steps": [
    ("Attach Listeners", "page.on('console') and page.on('pageerror') capture all errors"),
    ("try block", "Wrap all automation steps inside try:"),
    ("Catch TimeoutError", "from playwright.sync_api import TimeoutError as PWTimeout"),
    ("Catch General", "except Exception as e catches all other failures"),
    ("Screenshot on Fail", "page.screenshot(path='error.png') inside except block"),
    ("finally block", "browser.close() always runs — no zombie processes"),
],
"edge_cases": [
    ("Retry on Timeout", "Wrap action in for loop: for attempt in range(3): try: ... reload()"),
    ("Stale Selector", "Re-query locator inside retry — old reference may be stale after reload"),
    ("Network Mock Failure", "page.route('**/api/**', r.abort()) tests error states"),
    ("CI Screenshot Naming", "Use timestamp: f'fail_{int(time.time())}.png' for unique names"),
],
"advanced_code": """\
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PWTimeout
import time

def retry(fn, attempts=3, delay=2):
    \"\"\"Generic retry wrapper for Playwright actions.\"\"\"
    last_err = None
    for i in range(1, attempts + 1):
        try:
            return fn()
        except (PWTimeout, Exception) as e:
            print(f"  Attempt {i}/{attempts} failed: {e}")
            last_err = e
            time.sleep(delay)
    raise last_err

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        logs = {"console": [], "errors": [], "requests": []}
        page.on("console",   lambda m: logs["console"].append(m.text))
        page.on("pageerror", lambda e: logs["errors"].append(str(e)))
        page.on("request",   lambda r: logs["requests"].append(r.url))

        try:
            def perform():
                page.goto(
                    "https://demoqa.com/dynamic-properties",
                    wait_until="networkidle",
                    timeout=12000
                )
                page.wait_for_selector(
                    "#enableAfter:not([disabled])", timeout=8000
                )
                page.click("#enableAfter")

            retry(perform, attempts=3, delay=2)
            print("✅ Action completed!")

        except Exception as e:
            ts = int(time.time())
            page.screenshot(path=f"failure_{ts}.png")
            print(f"❌ All retries failed: {e}")
            print(f"Total requests made: {len(logs['requests'])}")
            print(f"JS errors: {logs['errors']}")

        finally:
            browser.close()

run()
""",
"expected_behavior": [
    "Console and pageerror listeners attached at startup",
    "First attempt loads page and waits for dynamic element",
    "On timeout: screenshot saved, retry fires after 2s delay",
    "On success: confirmation printed and browser closes cleanly",
    "On total failure: timestamped screenshot + error summary printed",
],
},

}

# ─────────────────────────────────────────────────────────────────────────────
#  KEYWORD ROUTING
# ─────────────────────────────────────────────────────────────────────────────

KEYWORD_MAP = {
    "login":    ["login","sign in","signin","auth","password","credential","log in"],
    "signup":   ["signup","sign up","register","registration","create account","new user"],
    "click":    ["click","button","modal","popup","dialog","alert","confirm","double click","right click"],
    "iframe":   ["iframe","frame","embed","embedded","tinymce","payment widget"],
    "scroll":   ["scroll","infinite","infinite scroll","feed","lazy load","scroll to"],
    "dropdown": ["dropdown","select","option","combo","combobox","picklist"],
    "hover":    ["hover","menu","tooltip","flyout","mouseover","submenu"],
    "waits":    ["wait","sync","network idle","timeout","async","loading","dynamic"],
    "upload":   ["upload","file","drag","drop","attachment","download"],
    "errors":   ["error","retry","exception","fail","handle error","try catch","robust"],
}

def detect_category(query: str):
    q = query.lower()
    for cat, keywords in KEYWORD_MAP.items():
        if any(kw in q for kw in keywords):
            return cat
    return None

# ─────────────────────────────────────────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    """Render health check endpoint."""
    return jsonify({"status": "ok", "service": "playwrightai"}), 200

@app.route("/")
def index():
    return Response(HTML_PAGE, mimetype="text/html")

@app.route("/generate", methods=["POST"])
def generate():
    body  = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"error": "Query is empty"}), 400
    cat = detect_category(query)
    if cat and cat in TEMPLATES:
        return jsonify({"status": "ok", "category": cat, "data": TEMPLATES[cat]})
    return jsonify({
        "status": "no_match",
        "message": f'No template found for: "{query}". Try one of these:',
        "suggestions": list(TEMPLATES.keys()),
    })

@app.route("/download", methods=["POST"])
def download():
    body     = request.get_json(silent=True) or {}
    code     = body.get("code", "")
    filename = body.get("filename", "automation.py")
    buf = io.BytesIO(code.encode("utf-8"))
    buf.seek(0)
    return send_file(buf, mimetype="text/plain",
                     as_attachment=True, download_name=filename)

@app.route("/categories")
def categories():
    return jsonify({k: v["title"] for k, v in TEMPLATES.items()})

# ─────────────────────────────────────────────────────────────────────────────
#  SELF-CONTAINED HTML (zero CDN — works offline and on Render)
# ─────────────────────────────────────────────────────────────────────────────

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PlaywrightAI — Automation CheatSheet Generator</title>
<style>
:root{
  --bg:#080810;--card:#13131e;--card2:#191926;
  --border:#252535;--border2:#2e2e44;
  --accent:#00ff88;--accent-d:#00cc6a;
  --text:#e4e4f0;--muted:#606078;--code-bg:#0a0a12;
  --glow:rgba(0,255,136,.18);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;line-height:1.6;padding:env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left)}
body::after{content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:linear-gradient(rgba(0,255,136,.022) 1px,transparent 1px),linear-gradient(90deg,rgba(0,255,136,.022) 1px,transparent 1px);
  background-size:48px 48px}
header{position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;
  padding:.85rem 2rem;background:rgba(8,8,16,.93);backdrop-filter:blur(16px);border-bottom:1px solid var(--border)}
.logo{display:flex;align-items:center;gap:.65rem}
.logo-icon{width:32px;height:32px;background:var(--accent);color:#000;border-radius:8px;
  display:flex;align-items:center;justify-content:center;font-size:.95rem;font-weight:700;box-shadow:0 0 18px var(--glow)}
.logo-text{font-size:1.15rem;font-weight:800;letter-spacing:-.02em}
.logo-text span{color:var(--accent)}
.badge{font-size:.58rem;letter-spacing:.1em;color:#a78bfa;background:rgba(124,58,237,.15);
  border:1px solid rgba(124,58,237,.25);padding:.22rem .55rem;border-radius:100px;font-family:monospace}
.hero{position:relative;z-index:1;max-width:820px;margin:0 auto;padding:3.5rem 2rem 2rem;text-align:center}
.hero-tag{display:inline-flex;align-items:center;gap:.4rem;font-size:.68rem;letter-spacing:.14em;
  text-transform:uppercase;color:var(--accent);border:1px solid rgba(0,255,136,.22);
  padding:.28rem .8rem;border-radius:100px;margin-bottom:1.3rem;font-family:monospace}
.dot{width:6px;height:6px;background:var(--accent);border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.7)}}
h1{font-size:clamp(1.9rem,5vw,3.2rem);font-weight:800;line-height:1.06;letter-spacing:-.03em;margin-bottom:.9rem}
h1 em{font-style:normal;color:var(--accent)}
.hero-sub{font-size:.97rem;color:var(--muted);max-width:480px;margin:0 auto 2.2rem}
.search-wrap{position:relative;max-width:680px;margin:0 auto 1.6rem}
.si{position:absolute;left:.95rem;top:50%;transform:translateY(-50%);width:17px;height:17px;color:var(--muted);pointer-events:none}
.search-input{width:100%;background:var(--card);border:1px solid var(--border2);border-radius:14px;
  padding:.95rem 148px .95rem 2.7rem;font-size:.93rem;color:var(--text);outline:none;
  transition:border-color .2s,box-shadow .2s;font-family:inherit}
.search-input:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(0,255,136,.1)}
.search-input::placeholder{color:var(--muted)}
.search-btn{position:absolute;right:5px;top:50%;transform:translateY(-50%);background:var(--accent);color:#000;
  border:none;border-radius:10px;padding:.62rem 1.15rem;font-weight:700;font-size:.82rem;cursor:pointer;
  white-space:nowrap;transition:background .2s,box-shadow .2s;font-family:inherit}
.search-btn:hover{background:var(--accent-d);box-shadow:0 0 22px rgba(0,255,136,.4)}
.search-btn:disabled{opacity:.5;cursor:not-allowed}
.cats{display:flex;flex-wrap:wrap;gap:.4rem;justify-content:center}
.cat-pill{font-size:.69rem;padding:.38rem .82rem;border-radius:100px;
  border:1px solid var(--border2);background:transparent;color:var(--muted);cursor:pointer;transition:all .2s;font-family:inherit}
.cat-pill:hover,.cat-pill.active{border-color:var(--accent);color:var(--accent);background:rgba(0,255,136,.07)}
.out{position:relative;z-index:1;max-width:920px;margin:0 auto;padding:0 1.5rem 5rem}
.empty-state{text-align:center;padding:5rem 2rem;color:var(--muted)}
.empty-icon{font-size:2.8rem;margin-bottom:.9rem;opacity:.3}
.empty-state h3{font-size:1.05rem;font-weight:700;color:var(--text);opacity:.4;margin-bottom:.45rem}
.empty-state p{font-size:.84rem}
.loading-state{display:flex;flex-direction:column;align-items:center;gap:.9rem;padding:4rem 2rem}
.spinner{width:36px;height:36px;border:2px solid var(--border2);border-top-color:var(--accent);
  border-radius:50%;animation:spin .75s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-lbl{font-size:.7rem;letter-spacing:.12em;color:var(--accent);font-family:monospace}
.err-card{background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.25);border-radius:12px;
  padding:1.3rem;color:#fca5a5;font-size:.88rem;line-height:1.65;animation:fi .3s}
.res-hd{background:var(--card);border:1px solid var(--border2);border-left:3px solid var(--accent);
  border-radius:14px;padding:1.3rem 1.5rem;margin-bottom:1.1rem;animation:si .35s ease}
.res-q{font-size:.66rem;letter-spacing:.1em;color:var(--muted);text-transform:uppercase;margin-bottom:.28rem;font-family:monospace}
.res-t{font-size:1.3rem;font-weight:700;letter-spacing:-.01em}
.res-c{font-size:.7rem;color:var(--muted);margin-top:.2rem}
.tags{display:flex;gap:.38rem;flex-wrap:wrap;margin-top:.55rem}
.tag{font-size:.58rem;letter-spacing:.06em;padding:.18rem .5rem;border-radius:5px;font-family:monospace}
.tg{background:rgba(0,255,136,.1);color:var(--accent)}
.tp{background:rgba(124,58,237,.1);color:#a78bfa}
.to{background:rgba(249,115,22,.1);color:#fb923c}
.sc{background:var(--card);border:1px solid var(--border);border-radius:12px;margin-bottom:.9rem;
  overflow:hidden;animation:si .35s ease both}
.sc:nth-child(2){animation-delay:.04s}.sc:nth-child(3){animation-delay:.08s}
.sc:nth-child(4){animation-delay:.12s}.sc:nth-child(5){animation-delay:.16s}
.sc:nth-child(6){animation-delay:.20s}.sc:nth-child(7){animation-delay:.24s}
@keyframes si{from{opacity:0;transform:translateY(13px)}to{opacity:1;transform:translateY(0)}}
@keyframes fi{from{opacity:0}to{opacity:1}}
.sh{display:flex;align-items:center;justify-content:space-between;padding:.88rem 1.25rem;
  cursor:pointer;user-select:none;border-bottom:1px solid transparent;transition:background .15s}
.sh:hover{background:rgba(255,255,255,.02)}
.sh.open{border-bottom-color:var(--border)}
.sl{display:flex;align-items:center;gap:.6rem;font-weight:700;font-size:.86rem}
.sic{width:26px;height:26px;border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:.85rem;flex-shrink:0}
.ia{background:rgba(0,255,136,.12)}.ib{background:rgba(249,115,22,.12)}.ic{background:rgba(124,58,237,.12)}
.id{background:rgba(59,130,246,.12)}.ie{background:rgba(239,68,68,.12)}.if_{background:rgba(234,179,8,.12)}
.chev{width:14px;height:14px;color:var(--muted);flex-shrink:0;transition:transform .2s}
.chev.open{transform:rotate(180deg)}
.sb{display:none;padding:1.2rem}
.sb.open{display:block}
.prose{font-size:.86rem;line-height:1.75;color:#b8b8cc}
.cw{background:var(--code-bg);border:1px solid rgba(255,255,255,.06);border-radius:9px;overflow:hidden;margin-bottom:.6rem}
.ct{display:flex;align-items:center;justify-content:space-between;padding:.5rem .85rem;
  background:rgba(255,255,255,.02);border-bottom:1px solid rgba(255,255,255,.05)}
.cl{font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-family:monospace}
.cpb{font-size:.6rem;letter-spacing:.05em;color:var(--accent);background:rgba(0,255,136,.07);
  border:1px solid rgba(0,255,136,.2);padding:.25rem .6rem;border-radius:5px;cursor:pointer;font-family:monospace}
.cpb:hover{background:rgba(0,255,136,.14);border-color:var(--accent)}
.cpb.ok{background:rgba(0,255,136,.25);color:#fff}
pre{margin:0!important;overflow-x:auto}
pre code{font-family:'Cascadia Code','Fira Code',Consolas,monospace!important;font-size:.76rem!important;
  line-height:1.68!important;padding:1.05rem!important;display:block;white-space:pre}
.hp{background:var(--code-bg);border:1px solid rgba(255,255,255,.06);border-radius:8px;
  padding:.9rem 1rem;margin-bottom:.7rem;font-family:monospace;font-size:.74rem;color:#8ab0d0;
  line-height:1.65;white-space:pre;overflow-x:auto}
.dlb{display:inline-flex;align-items:center;gap:.4rem;margin-top:.7rem;font-size:.68rem;
  letter-spacing:.05em;color:var(--accent);background:transparent;
  border:1px solid rgba(0,255,136,.22);padding:.42rem .85rem;border-radius:7px;cursor:pointer;
  transition:all .2s;font-family:monospace}
.dlb:hover{background:rgba(0,255,136,.08);border-color:var(--accent);box-shadow:0 0 14px rgba(0,255,136,.15)}
.steps{display:flex;flex-direction:column;gap:.65rem}
.step{display:flex;gap:.75rem;align-items:flex-start}
.sn{width:21px;height:21px;border-radius:50%;background:rgba(0,255,136,.1);
  border:1px solid rgba(0,255,136,.22);color:var(--accent);font-family:monospace;font-size:.58rem;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:2px}
.st{font-size:.84rem;line-height:1.55;color:#b8b8cc}
.st strong{color:var(--text)}
.st code{font-family:monospace;font-size:.78em;background:rgba(255,255,255,.07);padding:.1rem .28rem;border-radius:4px;color:#8ad8b0}
.eg{display:grid;grid-template-columns:1fr 1fr;gap:.65rem;margin-bottom:1.1rem}
@media(max-width:560px){.eg{grid-template-columns:1fr}}
.ec{background:rgba(249,115,22,.04);border:1px solid rgba(249,115,22,.14);border-radius:8px;padding:.8rem}
.ec h4{font-size:.73rem;font-weight:700;color:#fb923c;margin-bottom:.28rem}
.ec p{font-size:.76rem;color:var(--muted);line-height:1.5}
.bl{list-style:none}
.bl li{display:flex;align-items:flex-start;gap:.55rem;padding:.42rem 0;
  border-bottom:1px solid rgba(255,255,255,.04);font-size:.84rem;color:#b8b8cc;line-height:1.5}
.bl li:last-child{border-bottom:none}
.bl li::before{content:'→';color:var(--accent);font-family:monospace;font-size:.73rem;flex-shrink:0;margin-top:1px}
.nm{background:rgba(124,58,237,.06);border:1px solid rgba(124,58,237,.22);border-radius:12px;padding:1.3rem;animation:fi .3s}
.nm h3{font-size:.97rem;font-weight:700;color:#c4b5fd;margin-bottom:.45rem}
.nm p{font-size:.83rem;color:var(--muted);margin-bottom:.85rem}
.sg{display:flex;flex-wrap:wrap;gap:.38rem}
.sp{font-size:.67rem;padding:.28rem .7rem;border-radius:100px;
  border:1px solid rgba(124,58,237,.3);background:rgba(124,58,237,.07);color:#a78bfa;cursor:pointer;
  transition:all .15s;text-transform:capitalize;font-family:monospace}
.sp:hover{background:rgba(124,58,237,.15);border-color:rgba(124,58,237,.5)}
footer{position:relative;z-index:1;text-align:center;padding:1.4rem;border-top:1px solid var(--border);
  font-size:.63rem;letter-spacing:.07em;color:var(--muted);font-family:monospace}
footer span{margin:0 .4rem}
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px}
/* built-in syntax highlight */
.kw{color:#c678dd}.str{color:#98c379}.cm{color:#5c6370;font-style:italic}
.num{color:#d19a66}.fn{color:#61afef}.bi{color:#e5c07b}
/* ---------------------------------------------------
   ANDROID & MOBILE RESPONSIVE OVERRIDES
------------------------------------------------------ */
@media(max-width: 768px) {
  header { padding: .7rem 1.2rem; }
  .logo-text { font-size: 1.05rem; }
  .badge { display: none; }
  .hero { padding: 2.5rem 1.2rem 1.5rem; }
  h1 { font-size: 2.2rem; }
  .search-input { padding-left: 2.5rem; padding-right: 125px; }
  .search-btn { padding: .55rem 1rem; font-size: .8rem; }
  .out { padding: 0 1.2rem 4rem; }
}

@media(max-width: 480px) {
  h1 { font-size: 1.95rem; line-height: 1.1; }
  .hero-tag { font-size: .6rem; padding: .25rem .6rem; margin-bottom: 1rem; }
  .hero-sub { font-size: .88rem; margin-bottom: 1.8rem; }
  .search-wrap { display: flex; flex-direction: column; gap: 0.8rem; }
  .search-input { width: 100%; border-radius: 12px; padding: 1rem 1rem 1rem 2.8rem; font-size: 1rem; }
  .si { top: 1.15rem; transform: none; }
  .search-btn { position: relative; right: auto; top: auto; transform: none; width: 100%; padding: 1rem; border-radius: 12px; font-size: .95rem; min-height: 48px; }
  .cat-pill { padding: .55rem 1rem; font-size: .8rem; min-height: 42px; border-radius: 100px; display:inline-flex; align-items:center; justify-content:center; }
  .res-hd, .sc { border-radius: 10px; }
  .res-hd { padding: 1.1rem; }
  .sh { padding: .95rem 1.1rem; min-height: 48px; }
  .sb { padding: 1rem; }
  pre code { font-size: .72rem !important; padding: .9rem !important; }
  footer { display: flex; flex-direction: column; gap: .5rem; font-size: .65rem; }
  footer span { display: block; margin: 0; }
  footer span:nth-child(even) { display: none; }
  .cpb { min-height: 36px; padding: .35rem .75rem; }
  .dlb { min-height: 42px; padding: .5rem .95rem; }
  .sp { min-height: 36px; padding: .4rem .8rem; }
}
</style>
</head>
<body>
<header>
  <div class="logo">
    <div class="logo-icon">▶</div>
    <div class="logo-text">Playwright<span>AI</span></div>
  </div>
  <span class="badge">AUTOMATION CHEATSHEET GENERATOR</span>
</header>

<section class="hero">
  <div class="hero-tag"><span class="dot"></span>&nbsp;AI-Powered · Python · Playwright</div>
  <h1>Generate <em>Playwright</em><br>Code Instantly</h1>
  <p class="hero-sub">Type any web automation task — get working Python code, step-by-step guide, edge cases &amp; advanced patterns.</p>
  <div class="search-wrap">
    <svg class="si" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
    <input class="search-input" id="qi" type="text"
      placeholder="e.g. login form, iframe, infinite scroll, file upload..."
      autocomplete="off"/>
    <button class="search-btn" id="genBtn" onclick="generate()">⚡ Generate</button>
  </div>
  <div class="cats">
    <button class="cat-pill" onclick="setQ('automate login form')">🔐 Login</button>
    <button class="cat-pill" onclick="setQ('signup form automation')">📝 Signup</button>
    <button class="cat-pill" onclick="setQ('click button handle modal')">🖱️ Click</button>
    <button class="cat-pill" onclick="setQ('handle iframe content')">📦 iFrame</button>
    <button class="cat-pill" onclick="setQ('infinite scroll page')">📜 Scroll</button>
    <button class="cat-pill" onclick="setQ('handle dropdown select')">⬇️ Dropdown</button>
    <button class="cat-pill" onclick="setQ('hover menu navigation')">🧭 Hover</button>
    <button class="cat-pill" onclick="setQ('wait for network idle')">⏱️ Waits</button>
    <button class="cat-pill" onclick="setQ('file upload automation')">📎 Upload</button>
    <button class="cat-pill" onclick="setQ('error handling retry logic')">⚠️ Errors</button>
  </div>
</section>

<div class="out" id="output">
  <div class="empty-state">
    <div class="empty-icon">⚙️</div>
    <h3>Ready to automate</h3>
    <p>Pick a category above or type your query and press Enter.</p>
  </div>
</div>

<footer>
  <span>PlaywrightAI</span><span>·</span>
  <span>Flask + Playwright + Python</span><span>·</span>
  <span>10 Automation Modules</span>
</footer>

<script>
/* ── util ──────────────────────────────────────── */
function esc(s){
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function setQ(t){ document.getElementById('qi').value=t; generate(); }
document.getElementById('qi').addEventListener('keydown',e=>{ if(e.key==='Enter') generate(); });

/* ── syntax highlight ─────────────────────────── */
function hl(code){
  var safe=code.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  var KW='from|import|def|class|with|as|for|while|if|elif|else|try|except|finally|return|raise|pass|break|continue|and|or|not|in|is|lambda|True|False|None|assert';
  var BI='print|range|len|str|int|list|dict|set|type|open|isinstance|hasattr|getattr|vars|uuid';
  return safe
    .replace(new RegExp('(#[^\n]*)','g'),'<span class="cm">$1</span>')
    .replace(new RegExp('\\b('+KW+')\\b','g'),'<span class="kw">$1</span>')
    .replace(new RegExp('\\b('+BI+')\\b','g'),'<span class="bi">$1</span>')
    .replace(new RegExp('\\b([A-Za-z_]\\w*)(?=\\()','g'),'<span class="fn">$1</span>')
    .replace(new RegExp('\\b(\\d+)\\b','g'),'<span class="num">$1</span>');
}

/* ── code block ───────────────────────────────── */
function codeBlock(code){
  const id='cb_'+Math.random().toString(36).slice(2);
  return `<div class="cw">
    <div class="ct">
      <span class="cl">python</span>
      <button class="cpb" onclick="cpCode('${id}',this)">⎘ Copy</button>
    </div>
    <pre><code id="${id}">${hl(code)}</code></pre>
  </div>`;
}

function cpCode(id,btn){
  const raw=(document.getElementById(id).innerText||'');
  navigator.clipboard.writeText(raw).then(()=>{
    btn.textContent='✓ Copied!'; btn.classList.add('ok');
    setTimeout(()=>{btn.textContent='⎘ Copy';btn.classList.remove('ok');},2000);
  });
}

/* ── download ─────────────────────────────────── */
function dlPy(code,fname){
  fetch('/download',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({code,filename:fname})})
  .then(r=>r.blob()).then(blob=>{
    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob); a.download=fname; a.click();
  }).catch(()=>{
    const a=document.createElement('a');
    a.href='data:text/plain;charset=utf-8,'+encodeURIComponent(code);
    a.download=fname; a.click();
  });
}

/* ── toggle section ───────────────────────────── */
function tog(h){
  const b=h.nextElementSibling, c=h.querySelector('.chev');
  const o=b.classList.toggle('open');
  h.classList.toggle('open',o); c.classList.toggle('open',o);
}

/* ── generate ─────────────────────────────────── */
function generate(){
  const q=document.getElementById('qi').value.trim();
  if(!q) return;
  const btn=document.getElementById('genBtn');
  btn.disabled=true; btn.textContent='⏳ Generating...';
  document.getElementById('output').innerHTML=`
    <div class="loading-state">
      <div class="spinner"></div>
      <div class="loading-lbl">BUILDING CHEATSHEET...</div>
    </div>`;
  fetch('/generate',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({query:q})})
  .then(r=>r.json())
  .then(res=>{
    if(res.status==='ok') render(q,res.data);
    else renderNM(res.message,res.suggestions||[]);
  })
  .catch(e=>{
    document.getElementById('output').innerHTML=
      `<div class="err-card"><strong>⚠️ Request failed</strong><br>${esc(e.message)}</div>`;
  })
  .finally(()=>{ btn.disabled=false; btn.textContent='⚡ Generate'; });
}

function renderNM(msg,sugs){
  const pills=sugs.map(s=>`<span class="sp" onclick="setQ('${s}')">${s}</span>`).join('');
  document.getElementById('output').innerHTML=
    `<div class="nm"><h3>🔍 No exact match</h3><p>${esc(msg)}</p><div class="sg">${pills}</div></div>`;
}

/* ── render result ────────────────────────────── */
function render(q,r){
  const stH=(r.steps||[]).map((s,i)=>{
    const [title,text]=Array.isArray(s)?s:['Step',''];
    return `<div class="step"><div class="sn">${i+1}</div>
      <div class="st"><strong>${esc(title)}:</strong> ${text}</div></div>`;
  }).join('');

  const egH=(r.edge_cases||[]).map(e=>{
    const [t,d]=Array.isArray(e)?e:['',''];
    return `<div class="ec"><h4>${esc(t)}</h4><p>${esc(d)}</p></div>`;
  }).join('');

  const bhH=(r.expected_behavior||[]).map(b=>`<li>${esc(b)}</li>`).join('');

  const pyC=r.playwright_code||'';
  const adC=r.advanced_code||'';
  const fn=(r.title||q).toLowerCase().replace(/\s+/g,'_')+'.py';

  const secs=[
    {icon:'📌',ic:'ia',open:true, lbl:'Section A — Use Case',
     body:`<div class="prose">${esc(r.use_case||'')}</div>`},
    {icon:'🌐',ic:'ib',open:true, lbl:'Section B — HTML Structure',
     body:`<div class="hp">${esc(r.html_example||'')}</div>
           <p class="prose" style="font-size:.77rem;color:var(--muted)">Target HTML structure your script will interact with.</p>`},
    {icon:'💻',ic:'ic',open:true, lbl:'Section C — Playwright Code (Copy-Ready)',
     body:`${codeBlock(pyC)}<button class="dlb" onclick="dlPy(${JSON.stringify(pyC)},'${fn}')">⬇ Download .py</button>`},
    {icon:'📖',ic:'id',open:false, lbl:'Section D — Step-by-Step Breakdown',
     body:`<div class="steps">${stH}</div>`},
    {icon:'🚀',ic:'ie',open:false, lbl:'Section E — Advanced Version & Edge Cases',
     body:`<div class="eg">${egH}</div>
           <p class="prose" style="font-size:.8rem;margin-bottom:.85rem">Advanced: error handling, retries &amp; robust patterns:</p>
           ${codeBlock(adC)}`},
    {icon:'✅',ic:'if_',open:false, lbl:'Section F — Expected Behaviour',
     body:`<ul class="bl">${bhH}</ul>`},
  ];

  const secsH=secs.map(s=>`
    <div class="sc">
      <div class="sh ${s.open?'open':''}" onclick="tog(this)">
        <div class="sl"><div class="sic ${s.ic}">${s.icon}</div>${s.lbl}</div>
        <svg class="chev ${s.open?'open':''}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"/></svg>
      </div>
      <div class="sb ${s.open?'open':''}">${s.body}</div>
    </div>`).join('');

  document.getElementById('output').innerHTML=`
    <div class="res-hd">
      <div class="res-q">QUERY → "${esc(q)}"</div>
      <div class="res-t">${esc(r.title||q)}</div>
      <div class="res-c">${esc(r.category||'')}</div>
      <div class="tags">
        <span class="tag tg">✓ Playwright Sync API</span>
        <span class="tag tp">Python 3.x</span>
        <span class="tag to">Copy-Ready</span>
      </div>
    </div>${secsH}`;

  document.getElementById('output').scrollIntoView({behavior:'smooth',block:'start'});
}
</script>
</body>
</html>"""

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    print(f"\n{'='*52}\n  🚀  PlaywrightAI running!\n  👉  http://127.0.0.1:{port}\n{'='*52}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
