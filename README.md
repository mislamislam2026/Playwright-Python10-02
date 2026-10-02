# Web-Tours-RT

[![Web Tours UI Tests](https://github.com/mislamislam2026/Web-Tours-RT/actions/workflows/ui-tests.yml/badge.svg)](https://github.com/mislamislam2026/Web-Tours-RT/actions/workflows/ui-tests.yml)

UI test automation for the Micro Focus / OpenText **Web Tours** demo application,
built with **Python, Pytest, Playwright and the Page Object Model**.

Default target: `http://192.168.1.183:1080/webtours/`

---

## 1. Project structure

```
Web-Tours-RT/
├── .github/workflows/
│   └── ui-tests.yml          # CI: lint + collect (cloud), UI tests (self-hosted)
├── config/
│   ├── __init__.py
│   └── settings.py          # URL, browser, timeouts, paths (env-overridable)
├── pages/                    # Page Objects: locators + actions + page assertions
│   ├── __init__.py
│   ├── base_page.py          # frame accessors + shared helpers
│   ├── home_page.py          # login form, menu, welcome message
│   ├── flights_page.py       # find flight → select → payment → invoice
│   ├── itinerary_page.py     # list / cancel reservations
│   └── registration_page.py  # "sign up now" customer profile
├── tests/                    # test cases only — no locators
│   ├── test_login.py
│   ├── test_flights.py
│   ├── test_itinerary.py
│   └── test_registration.py
├── test_data/
│   ├── users.json
│   └── flights.json
├── utils/
│   ├── __init__.py
│   ├── data_loader.py        # JSON test-data loading
│   ├── helpers.py            # unique usernames, dates, file names
│   └── logger.py
├── reports/                  # created at run time (HTML report, screenshots)
├── conftest.py               # fixtures, CLI options, failure screenshots
├── .flake8                   # PEP 8 lint settings
├── pytest.ini
├── requirements.txt          # runtime: playwright, pytest, pytest-html
├── requirements-dev.txt      # dev/CI: flake8
└── README.md
```

---

## 2. Installation

Python 3.9+ is required.

```bash
git clone https://github.com/mislamislam2026/Web-Tours-RT.git
cd Web-Tours-RT

# create and activate a virtual environment
python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt
playwright install            # downloads Chromium, Firefox and WebKit
# or just one engine:  playwright install chromium
```

Make sure the Web Tours server is running and reachable from this machine:
open `http://192.168.1.183:1080/webtours/` in a browser first.

---

## 3. Running the tests

| Command | What it does |
|---|---|
| `pytest` | Run every test (headless Chromium) |
| `pytest -v` | Verbose: one line per test |
| `pytest -m smoke` | Critical-path checks only |
| `pytest -m regression` | Full functional suite |
| `pytest -m login` | Login/logout scenarios |
| `pytest -m negative` | Invalid-input / error-handling tests |
| `pytest -m "regression and not negative"` | Combine markers |
| `pytest --headed` | Show the browser window |
| `pytest --headed --slowmo 500` | Watch it step by step |
| `pytest --browser-name firefox` | Use Firefox (or `webkit`) |
| `pytest --base-url http://host:1080/webtours/` | Point at another server |
| `pytest tests/test_login.py` | One file |
| `pytest -k "invalid_credentials"` | Tests whose name matches |
| `pytest -x` | Stop at the first failure |

The same settings can be given as environment variables:
`BASE_URL`, `BROWSER`, `HEADLESS=false`, `SLOW_MO`, `DEFAULT_TIMEOUT`, `NAVIGATION_TIMEOUT`.

### Reports and screenshots

* HTML report: `reports/report.html` (self-contained; failure screenshots are embedded).
* When a test fails, a full-page screenshot is saved to `reports/screenshots/`.

---

## 4. Test data and state

* The default account is Web Tours' built-in `jojo` / `bean` (`test_data/users.json`).
* Booking and itinerary tests use the `empty_itinerary` fixture, which cancels all
  of the user's reservations before **and after** the test so runs are repeatable.
* Registration tests create a unique username every run (`utils.helpers.unique_username`).

---

## 5. Continuous integration (GitHub Actions)

The workflow is `.github/workflows/ui-tests.yml`. It has two jobs:

| Job | Runner | When | What it does |
|---|---|---|---|
| **Lint & collect tests** | GitHub-hosted `ubuntu-latest` | every push and PR to `main` | flake8, then `pytest --collect-only` to catch broken imports, fixtures or markers |
| **UI tests** | **self-hosted**, labels `self-hosted, webtours` | push to `main`, weekdays 07:00 New York time, or by hand | installs Playwright, checks the app is reachable, runs the tests, uploads `reports/` (HTML report, JUnit XML, screenshots) |

### Why a self-hosted runner?

`192.168.1.183` is a private LAN address. GitHub's cloud runners are on the
internet and cannot reach it. The UI tests therefore run on a machine inside
your network: the Web Tours server itself or any PC that can open the URL.

### One-time setup

1. **Register the runner.** In the repository, go to **Settings → Actions → Runners → New self-hosted runner**.
   Pick the OS of your machine and run the commands GitHub shows. When `config` asks for
   extra labels, enter `webtours`. Then start it with `run.cmd` / `./run.sh`, or install
   it as a service (`svc install` on Linux, or answer *Y* to the service prompt on Windows).
2. The runner machine needs **Python 3.9+** on the PATH (or let `actions/setup-python`
   install it). On Linux, run once: `sudo python -m playwright install-deps`.
3. **Turn the UI job on.** Go to **Settings → Secrets and variables → Actions → Variables** and add:
   * `RUN_UI_TESTS` = `true`
   * `BASE_URL` = `http://192.168.1.183:1080/webtours/` (optional; this is the default)

Until `RUN_UI_TESTS` is `true`, the UI job is skipped. This means pushes never sit
waiting for a runner that does not exist yet.

### Running it by hand

Go to **Actions → Web Tours UI Tests → Run workflow**. Choose a marker
(`smoke`, `regression`, `login`, `negative`, `smoke or regression`), a browser,
and optionally a different URL.

### Results

Open a run and download the **ui-test-report-…** artifact. It contains
`report.html` (with screenshots embedded) and `screenshots/`.

---

## 6. POM architecture

```
tests/  ──uses──▶  fixtures (conftest.py)  ──create──▶  Page Objects (pages/)
                                                          │
                                                          ▼
                                                 BasePage (frames, helpers)
                                                          │
                                                          ▼
                                                 Playwright Page / FrameLocator
```

* **Tests describe behavior.** A test reads like a scenario: log in, search, book,
  check the itinerary. It never contains a selector.
* **Page Objects own the UI.** Each class exposes:
  * **locators** as read-only properties (`username_input`, `login_button` …),
  * **actions** (`login()`, `search()`, `book_flight()`, `cancel_all_flights()`),
  * **page-level assertions** (`expect_logged_in_as()`, `expect_booking_confirmed()`),
    built on Playwright's auto-retrying `expect`.
  When the UI changes, only the page object changes.
* **BasePage handles frames.** Web Tours is a frameset (`body` → `navbar` + `info`).
  `BasePage.navbar` and `BasePage.info` return `FrameLocator`s. They are resolved
  again on every action, so they keep working when a frame reloads after a click.
* **Fixtures own the lifecycle.** The browser is launched once per session.
  Each test gets a fresh `BrowserContext` (isolated cookies) and `Page`, which are
  closed automatically. State fixtures (`logged_in`, `empty_itinerary`) compose on top.
* **Data lives outside code.** JSON files in `test_data/` feed parametrised tests.

### Locator strategy

The suite prefers `get_by_role` / `get_by_text`. Image buttons such as Login are
found by role and their alt text. Web Tours is a legacy app with **no `<label>`
elements**, so `get_by_label` has nothing to match. Form fields therefore use their
stable `name` attribute (`input[name="username"]`). CSS is also needed for frame
selection. All of these are documented in the page objects.

### Waiting strategy

There are no `sleep` calls. The suite relies on Playwright's auto-waiting actions and
`expect(...)` assertions, which retry until `DEFAULT_TIMEOUT` (10 s).

---

## 7. If a locator does not match your Web Tours build

Web Tours versions differ slightly in markup. If a test fails on "element not found":

1. Run `pytest --headed -x` or open the failure screenshot in `reports/screenshots/`.
2. Run `playwright codegen http://192.168.1.183:1080/webtours/` and click the element.
   Playwright suggests a locator for it.
3. Update the single matching property in `pages/*.py`. No test needs to change.

The negative tests for flights and registration (same city, past date, password
mismatch) assume Web Tours rejects that input. If your build accepts it, adjust or
remove those tests.

---

## 8. Extending the framework

* **New page:** subclass `BasePage` in `pages/`, add locators and actions, export
  it from `pages/__init__.py`, and add a fixture in `conftest.py`.
* **Faster log-in:** save the session once with `context.storage_state(path=...)`
  and pass `storage_state=` to `new_context` for tests that do not test login.
* **Parallel runs:** `pip install pytest-xdist`, then `pytest -n 4`. Give each worker
  its own user (registered on the fly), because tests share `jojo`'s itinerary.
* **Tracing:** call `context.tracing.start(screenshots=True, snapshots=True)` in the
  `context` fixture and save the trace on failure. Inspect it with `playwright show-trace`.
* **Video:** pass `record_video_dir="reports/videos"` to `new_context`.
* **Retries for flaky environments:** `pip install pytest-rerunfailures`, then
  `pytest --reruns 1`.
* **Allure reports:** `pip install allure-pytest`, then `pytest --alluredir=reports/allure`.
* **CI notifications:** add a Slack or Teams step after the UI job with `if: failure()`.
* **Test results in the PR:** publish `reports/junit.xml` with a JUnit reporter action.
* **Environments:** add `config/<env>.json` files and select one with `--env`.
* **Code quality:** add `ruff`/`black` and a pre-commit hook.
