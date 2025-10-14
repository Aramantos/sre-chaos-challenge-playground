# Architectural Diagrams

This document contains text-based diagrams that visually explain the local tracker's design and its isolation from the production environment.

## Diagram 1: Local Tracker Components and Data Flow

```
+--------------------+
| local-tracker-app  |
| (Angular Frontend) |
+----------+---------+
           |
           | (HTTP GET)
           v
+----------+---------+
| local-tracker-service |
| (Node.js Backend)  |
+----------+---------+
           ^         |
           |         | (HTTP POST)
(HTTP POST)|         v
           |   +-----+-----+
           |   | local-db  |
           |   | (PostgreSQL)|
           |   +-----------+
           |
+----------+---------+
| load-generator     |
| (Python Script)    |
+--------------------+
```

## Diagram 2: Isolation from Production Environment

```
+------------------------------------+
| Production Environment             |
|                                    |
| +-----------------+  +-------------+ |
| | Official Backend|  | Official DB | |
| +-----------------+  +-------------+ |
|                                    |
+----------------+-------------------+
                 |
                 | (No direct communication)
                 v
+----------------+-------------------+
| Local Development Environment      |
|                                    |
| +--------------------+
| | local-tracker-app  |
| +--------------------+
|           |
|           v
| +--------------------+
| | local-tracker-service |
| +--------------------+
|           |
|           v
| +--------------------+
| | local-db           |
| +--------------------+
|                                    |
+------------------------------------+
```
