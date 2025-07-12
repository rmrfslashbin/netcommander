# Synaccess netCommander Integration Project

This project aimed to create an OpenAPI specification and a Home Assistant custom component for the Synaccess netCommander device, based on the provided `1291_NPCStartup_v13.pdf` manual.

## Project Expectations

**Please Note:** As of the last attempt, the Home Assistant integration is **non-functional** due to persistent authentication challenges with the device's web interface. The OpenAPI specification serves as a conceptual mapping of the device's commands to a more standard API structure, but it cannot be directly used to interact with the device without first solving the underlying authentication problem.

This `README.md` documents the journey, the challenges faced, and potential avenues for future exploration.

## 1. Initial Analysis of `1291_NPCStartup_v13.pdf`

The `1291_NPCStartup_v13.pdf` manual describes a command-line interface (CLI) and a web/Telnet interface for the netCommander device. Key insights from the manual regarding the web interface (`HTTP/HTTPS`) were:

*   **Endpoint:** All commands are sent to `/cmd.cgi`.
*   **Command Format:** Commands are passed as a single query parameter, comma-separated: `http://my_IP_addr/cmd.cgi?cmdCode,Arg1,Arg2`.
*   **Command Codes:** Specific codes like `$A1` (Login), `$A3` (Set Outlet), `$A5` (Get Status), etc.
*   **Return Codes:** The device returns `$A0` for success and `$AF` for failure within the response body.
*   **Authentication Ambiguity:** The manual mentions a `Login` command (`$A1`) with username and password, but it's unclear how this interacts with standard HTTP authentication (e.g., Basic Auth, cookies). The web interface also has a login page.

## 2. OpenAPI Specification Generation

An OpenAPI v3 specification (`openapi.yaml`) was generated to provide a more structured, RESTful representation of the device's capabilities. This was intended to inform client development, abstracting away the non-standard `cmd.cgi` interface.

```yaml
# Snippet of openapi.yaml
openapi: 3.0.0
info:
  title: NetCommander API
  description: A more friendly OpenAPI specification for the Synaccess netCommander device, based on 1291_NPCStartup_v13.pdf. This spec provides a cleaner, more RESTful interface that can be mapped to the device's CGI commands.
  version: "1.0.0"
servers:
  - url: http://{ip_address}
    variables:
      ip_address:
        default: "192.168.1.100"
        description: "IP address of the netCommander device."

paths:
  /login:
    post:
      summary: "Log in to the device"
      description: "Corresponds to command $A1. In a real client, this would become `GET /cmd.cgi?cmd=$A1&Arg1={username}&Arg2={password}`"
      # ... (rest of the spec)
```

## 3. Home Assistant Component Development (Initial Plan)

The goal was to create a Home Assistant custom component to expose the device's outlets as `switch` entities and its sensors (current, temperature) as `sensor` entities.

The planned structure was:
```
custom_components/netcommander/
├── __init__.py
├── api.py
├── config_flow.py
├── const.py
├── coordinator.py
├── manifest.json
├── sensor.py
└── switch.py
```

## 4. Debugging and Iteration - The Authentication Challenge

The primary hurdle encountered was the device's authentication mechanism. Despite the credentials working in the web browser, the programmatic attempts consistently failed with `invalid_auth` errors in Home Assistant or `401 Unauthorized` responses during direct API testing.

### Attempt 1: Standard HTTP Parameters (Initial `api.py`)

*   **Approach:** Sent commands as standard HTTP query parameters (e.g., `?cmd=X&arg1=Y`).
*   **Problem:** Home Assistant reported `invalid_auth`.
*   **Hypothesis:** The device expects the comma-separated format as per the PDF.

### Attempt 2: Comma-Separated URL Parameters (v1.0.1)

*   **Approach:** Modified `api.py` to construct URLs with comma-separated arguments (e.g., `?cmdCode,Arg1,Arg2`).
*   **Problem:** Still `invalid_auth` in Home Assistant.
*   **Debugging Step:** Added detailed logging to `api.py` (v1.0.2) and created `test_api.py` for local, isolated testing.

#### `test_api.py` Output (v1.0.2)

```
--- Starting API Login Test ---
Attempting to log in to 192.168.50.227...

--- Test Result ---
❌ Login FAILED
--------------------
2025-07-12 11:59:08,254 - DEBUG - asyncio - Using selector: KqueueSelector
2025-07-12 11:59:08,254 - DEBUG - api - Login URL: http://192.168.50.227/cmd.cgi?$A1,admn,EdDMRNwHUDAv
2025-07-12 11:59:08,306 - DEBUG - api - Login response: 401 Unauthorized: Password required
```
*   **Insight:** The device was returning a `401 Unauthorized` HTTP status code, indicating a problem at the HTTP authentication layer, not just with the command format. This suggested HTTP Basic Authentication was required.

### Attempt 3: `aiohttp.BasicAuth`

*   **Approach:** Integrated `aiohttp.BasicAuth` into the `ClientSession` to send standard HTTP Basic Authentication headers.
*   **Problem:** Still received `401 Unauthorized` from the device.

#### `test_api.py` Output (after `aiohttp.BasicAuth` implementation)

```
--- Starting API Login Test ---
Attempting to log in to 192.168.50.227...

--- Test Result ---
❌ Login FAILED
--------------------
2025-07-12 12:49:55,561 - DEBUG - asyncio - Using selector: KqueueSelector
2025-07-12 12:49:55,561 - DEBUG - api - Login URL: http://192.168.50.227/cmd.cgi?$A1,admn,EdDMRNwHUDAv
2025-07-12 12:49:55,620 - DEBUG - api - Login response: 401 Unauthorized: Password required
```
*   **Insight:** The device was still rejecting the credentials at the HTTP level. This was highly unusual if standard Basic Auth was expected.

### Attempt 4: Manual Basic Auth Headers

*   **Approach:** Manually constructed the `Authorization` header using `base64` encoding, bypassing `aiohttp`'s helper, in case of subtle differences. Also tried sending the `$A1` login command simultaneously.
*   **Problem:** Received `401 Unauthorized` for the initial request, followed by a `500 Internal Server Error` when the `$A1` command was included.

#### `test_api.py` Output (after manual Basic Auth)

```
--- Starting API Login Test ---
Attempting to log in to 192.168.50.227...

--- Test Result ---
❌ Login FAILED
--------------------
2025-07-12 12:50:22,268 - DEBUG - asyncio - Using selector: KqueueSelector
2025-07-12 12:50:22,268 - DEBUG - api - Login URL: http://192.168.50.227/cmd.cgi
2025-07-12 12:50:22,365 - DEBUG - api - Login response status: 401
2025-07-12 12:50:22,365 - DEBUG - api - Login URL with command: http://192.168.50.227/cmd.cgi?$A1,admn,EdDMRNwHUDAv
2025-07-12 12:50:22,411 - DEBUG - api - Login response status with command: 500
```
*   **Insight:** The `500` error suggested the device was confused by receiving authentication information in multiple ways. This led to the hypothesis that the `$A1` command was *not* for HTTP authentication, but perhaps for Telnet, and that the web interface used standard HTTP Basic Auth *only*.

### Attempt 5: Pure HTTP Basic Auth, no `$A1` command (Refactored API to v2.0.0)

*   **Approach:** Completely refactored `api.py` to use only `aiohttp.BasicAuth` for all requests, removing any `cmd.cgi?$A1` calls for login. The `async_login` method simply tested the connection with Basic Auth.
*   **Problem:** Still received `401 Unauthorized`.

#### `test_api.py` Output (after pure Basic Auth refactor)

```
--- Starting Stateful API Test ---
Step 1: Logging in...
❌ Login FAILED

Step 3: Closing session...
--------------------------
2025-07-12 12:50:57,869 - DEBUG - asyncio - Using selector: KqueueSelector
2025-07-12 12:50:57,869 - DEBUG - api - Attempting to connect to http://192.168.50.227/cmd.cgi with Basic Auth
2025-07-12 12:50:58,053 - DEBUG - api - Login test response status: 401
```
*   **Insight:** This was the most perplexing. Standard HTTP Basic Auth was still failing, despite working in the browser. This pointed towards a non-standard authentication or a session/cookie-based mechanism.

### Attempt 6: Stateful `aiohttp.ClientSession` (Refactored API to v2.0.0 - second iteration)

*   **Approach:** Refactored `api.py` again to use a single, persistent `aiohttp.ClientSession` to handle cookies, mimicking browser behavior. The login attempt was directed to `/login.cgi` with POST data.
*   **Problem:** Received `404 Not Found` on `/login.cgi`.

#### `test_api.py` Output (after stateful session to `/login.cgi`)

```
--- Starting Stateful API Test ---
Step 1: Logging in...
❌ Login FAILED

Step 3: Closing session...
--------------------------
2025-07-12 13:45:10,178 - DEBUG - asyncio - Using selector: KqueueSelector
2025-07-12 13:45:10,178 - DEBUG - api - Attempting login to http://192.168.50.227/login.cgi
2025-07-12 13:45:10,255 - DEBUG - api - Login response status: 404
2025-07-12 13:45:10,255 - ERROR - api - Login failed. Status: 404, URL: http://192.168.50.227/login.cgi
```
*   **Insight:** The `404` indicated the login endpoint was incorrect. It was hypothesized that the root path (`/`) handled the login POST.

### Attempt 7: Stateful `aiohttp.ClientSession` to `/`

*   **Approach:** Changed the login POST target to the root URL (`/`).
*   **Problem:** Still received `401 Unauthorized`.

#### `test_api.py` Output (after stateful session to `/`)

```
--- Starting Stateful API Test ---
Step 1: Logging in...
❌ Login FAILED

Step 3: Closing session...
--------------------------
2025-07-12 13:45:24,613 - DEBUG - asyncio - Using selector: KqueueSelector
2025-07-12 13:45:24,613 - DEBUG - api - Attempting login to http://192.168.50.227/
2025-07-12 13:45:24,704 - DEBUG - api - Login response status: 401
2025-07-12 13:45:24,704 - ERROR - api - Login failed. Status: 401, URL: http://192.168.50.227/
```
*   **Insight:** This was the final straw for standard HTTP authentication. The device consistently returned `401` despite all standard attempts.

### Attempt 8: Re-reading PDF for "channel selection" (Stateless API, final iteration)

*   **Approach:** Reverted to a stateless API model, but added a speculative "channel selection" command (`/sset,1`) before the login, based on a vague mention in the serial port section of the PDF.
*   **Problem:** Still `401 Unauthorized` on both the channel select and login commands.

#### `test_api.py` Output (after channel selection attempt)

```
--- Starting Stateless API Test ---
Step 1: Sending Login Command...
❌ Login Command FAILED
--------------------------
2025-07-12 14:10:59,705 - DEBUG - asyncio - Using selector: KqueueSelector
2025-07-12 14:10:59,706 - DEBUG - api - Attempting to select channel with URL: http://192.168.50.227/cmd.cgi?/sset,1
2025-07-12 14:10:59,782 - DEBUG - api - Channel select response status: 401
2025-07-12 14:10:59,782 - DEBUG - api - Attempting login with URL: http://192.168.50.227/cmd.cgi?$A1,admn,EdDMRNwHUDAv
2025-07-12 14:10:59,825 - DEBUG - api - Login response status: 401, body: 401 Unauthorized: Password required
```

## 5. Conclusion and Future Exploration

The Synaccess netCommander device exhibits a highly non-standard and undocumented authentication mechanism for its web interface. Despite numerous attempts using various HTTP authentication methods (Basic Auth, session/cookies) and strictly adhering to the command format described in the PDF, programmatic login consistently failed with `401 Unauthorized` errors.

The device's behavior suggests:
*   It does not use standard HTTP Basic Authentication in a way that `aiohttp` can easily replicate.
*   The `login.cgi` or root (`/`) endpoints do not accept simple POST requests for authentication.
*   The `$A1` login command, while documented, does not appear to function as an HTTP authentication mechanism for the web interface.

**Points for Further Exploration (Requires Human Intervention):**

1.  **Deep Packet Inspection:** The most promising next step would be to use a tool like Wireshark to capture the exact HTTP requests and responses (including headers and body) exchanged between a web browser and the device during a successful login. This would reveal any custom headers, JavaScript-driven authentication flows, or non-standard authentication schemes.
2.  **Reverse-Engineering Web Interface JavaScript:** If the authentication is handled client-side, analyzing the JavaScript code served by the device's web interface could reveal the exact authentication logic.
3.  **Manufacturer Documentation:** Contacting Synaccess Networks directly for more detailed API documentation for their web interface would be the most straightforward solution, if available.

Without these insights, replicating the authentication programmatically is not feasible.

## Current Project State

The project has been reverted to its state before the extensive authentication debugging attempts (v1.0.2). The `openapi.yaml` file remains as a conceptual guide, and the Home Assistant component code is present but currently non-functional due to the unresolved authentication issue.