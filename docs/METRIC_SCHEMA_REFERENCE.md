# Internal Metric Schema Reference

This document defines the internal JSON schema used by the `local-tracker-service` and `load-generator` for automatic metric reporting. **Users do not need to send this data manually.**

This documentation is for contributors developing or extending the automation scripts, not for general users running the environment.

## Schema Definition

The `metrics_data` object should contain the following fields:

| Field                 | Type      | Description                                                                 |
| --------------------- | --------- | --------------------------------------------------------------------------- |
| `target_url`          | `string`  | The URL that was tested.                                                    |
| `request_count`       | `integer` | The total number of requests sent.                                          |
| `method`              | `string`  | The HTTP method used (e.g., 'GET', 'POST').                                 |
| `payload_urls`        | `array`   | A list of URLs used in the request payload (for POST requests).             |
| `total_requests`      | `integer` | The total number of requests made.                                          |
| `successful_requests` | `integer` | The number of successful requests.                                          |
| `failed_requests`     | `integer` | The number of failed requests.                                              |
| `avg_latency_ms`      | `float`   | The average latency in milliseconds.                                        |
| `error_rate`          | `float`   | The percentage of requests that failed.                                     |
| `rps`                 | `float`   | The number of requests per second.                                          |
| `duration_s`          | `float`   | The total duration of the test in seconds.                                  |
| `test_type`           | `string`  | A label to identify the type of test (e.g., "manual_load_test").          |

## Example

```json
{
    "target_url": "http://url-anvil:8080",
    "request_count": 100,
    "method": "GET",
    "payload_urls": [],
    "total_requests": 100,
    "successful_requests": 100,
    "failed_requests": 0,
    "avg_latency_ms": 123.45,
    "error_rate": 0.0,
    "rps": 10.0,
    "duration_s": 10.0,
    "test_type": "manual_load_test"
}
```
