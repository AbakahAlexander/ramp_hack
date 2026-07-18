# Crux: Route-Setting Intelligence for Climbing Gyms

## Hackathon submission

**Category:** Cursor — Best Community Impact Hack  
**Community:** Indoor climbers, routesetters, and climbing-gym staff

## One-line pitch

Crux gives climbing-gym staff one reliable view of their active routes and climber feedback, so they can build safer, more balanced, and more welcoming walls.

## Problem

Routesetting strongly shapes a climber's experience. It decides whether a new climber can find approachable routes, whether experienced climbers stay challenged, and whether the wall reflects a range of bodies, movement styles, and goals. Yet most gyms manage routes through a mix of staff memory, paper notes, spreadsheets, social posts, and scattered verbal feedback.

This leaves staff without clear answers to practical questions:

- Which routes are still engaging climbers, and which have become stale?
- Is each wall balanced across grades, styles, and accessibility needs?
- Are a route's assigned grade and the experience reported by climbers aligned?
- What feedback needs attention before the next reset?
- What should a routesetting team strip or set next?

Meanwhile, climbers often feel their feedback disappears. Newer climbers can struggle to find suitable climbs, while routesetters receive incomplete, anecdotal signals about how a route is landing.

## Opportunity and community impact

Crux makes routesetting more responsive to the community that uses the gym. It turns lightweight, opt-in climber input into organized staff insight while keeping the staff dashboard—not a public popularity contest—as the product's center of gravity.

Better wall decisions can lead to:

- More entry points for beginners and underrepresented climbers.
- More varied movement and grade coverage across the gym.
- Faster attention to routes that are confusing, uncomfortable, or potentially unsafe.
- A visible feedback loop that helps climbers feel heard.
- Fairer, more constructive coaching for routesetters.

## Product vision

Crux is a staff-facing operations dashboard for the full lifecycle of a climbing route: set it, understand how it performs, decide what to adjust, and archive what has been stripped.

Climbers interact through a minimal companion flow—normally a QR code at the route placard—to log an ascent or attempt and share a quick rating. Staff use the web dashboard to act on the aggregate data.

## Users

### Primary: routesetting manager

Plans setting cycles, maintains route inventory, checks wall coverage, and decides what should be reset. They need a fast view of priorities rather than another spreadsheet.

### Primary: routesetter

Records route intent and installation details, sees how a route has been received, and learns from contextual feedback over time.

### Secondary: front-desk or floor staff

Answers climber questions, captures reported issues, and helps keep the physical wall and route inventory in sync.

### Data contributor: climber

Uses a short mobile flow to mark a route as sent, attempted, or projected; optionally rates perceived difficulty and enjoyment; and can add feedback tags. This experience must take only a few seconds.

## Goals

- Give staff an accurate, searchable inventory of every active and archived route.
- Surface actionable route-health and wall-coverage signals.
- Help teams plan reset cycles based on evidence, not only memory.
- Close the loop on climber feedback without demanding a full social network.
- Evaluate routesetting work fairly by comparing like with like.

## Non-goals for the hackathon MVP

- A public climber leaderboard or setter popularity ranking.
- Automated grade assignment or safety certification.
- Replacement of a gym's membership, waiver, or access-control system.
- Detailed coaching analytics that require sensors, video, or paid hardware.
- A native mobile application; the climber flow is mobile web.

## Core experience

### 1. Staff dashboard: "What needs attention?"

The home screen provides an at-a-glance operational view:

| Module | Staff question answered | Example signal |
| --- | --- | --- |
| Wall health | Is the wall balanced? | The steep wall lacks beginner and intermediate routes. |
| Routes needing review | What needs a decision? | A 4-week-old route has a sharpness report and declining engagement. |
| Recent climber feedback | What are people saying? | Several climbers label a new V3 as "reachy" and harder than posted. |
| Upcoming work | What is planned? | Eight routes are due to be stripped in the next setting cycle. |
| Setting insights | Are we learning over time? | A setter's grades on slabs are consistently perceived one band harder. |

Staff can filter every module by location, zone, wall, grade band, style, setter, and set date.

### 2. Route inventory and route detail

Every active route has a canonical record. The route card shows a photo, location, color/hold identifier, setter(s), set date, assigned grade, style, and status. A detail view adds route history and feedback.

**Required route metadata**

- Route photo
- Location, zone, and wall
- Color or hold identifier
- Assigned grade and grade system
- Setter(s) and set date
- Route style tags (for example: slab, overhang, coordination, compression, technical)
- Status: active, needs review, scheduled for strip, or archived

**Route-health signals**

- Sends, attempts, projects, and unique contributors
- Perceived-grade distribution compared with assigned grade
- Enjoyment/quality rating with response count
- Recent feedback tags and free-text reports
- Age on wall and engagement trend
- Reset date or cycle

The page should always show sample size and feedback recency. A route with two ratings should not be presented as conclusively loved or disliked.

### 3. Fast climber feedback flow

A QR code on a placard opens the route's mobile page. The default contribution is intentionally small:

1. Choose **Sent**, **Tried**, or **Projecting**.
2. Optionally select perceived difficulty, enjoyment, and feedback tags.
3. Optionally leave a short comment or flag an issue.

Suggested tags include: fun, technical, powerful, reachy, morpho, confusing, sharp, sandbagged, soft, and great movement. Staff can customize their tag vocabulary.

The contribution is opt-in. A person can remain anonymous or attach their gym account if the gym chooses to support it. Individual-level activity is never shown in setter performance reporting.

### 4. Reset planner and wall coverage

The reset planner ranks active routes by a transparent, configurable review score. It combines route age, engagement trend, scheduled reset date, and issue reports. It is a prompt for staff judgment, not an automatic strip decision.

The coverage view maps active routes by wall, grade, and style. It highlights gaps such as "no easy slab routes" or "overhang routes concentrated in a single grade band," helping staff plan a setting day that serves more climbers.

### 5. Routesetter insights designed for learning

Setter analytics are private to authorized staff and framed as coaching context, not a public ranking. Metrics are compared only across similar route contexts, such as wall angle, intended grade, route age, and sufficient response volume.

Useful signals include:

- Grade calibration: difference between assigned and community-perceived grade.
- Route engagement: normalized sends/attempts and sustained activity.
- Quality feedback: enjoyment distribution and recurring feedback themes.
- Route mix: styles, walls, and grades a setter has contributed to.

The dashboard avoids a single "best setter" score. It should explain the underlying data and let managers recognize different setting strengths.

## Information architecture

```text
Staff dashboard
├── Overview
│   ├── Wall health
│   ├── Routes needing review
│   └── Upcoming setting work
├── Routes
│   ├── Active inventory
│   ├── Route detail and feedback
│   └── Archive
├── Plan
│   ├── Reset queue
│   └── Coverage matrix
├── Insights
│   ├── Route trends
│   └── Setter coaching view
└── Admin
    ├── Walls, grades, and tags
    ├── Team and roles
    └── QR placards
```

## Key user stories

- As a setting manager, I can see which routes need review so I can prioritize the next reset.
- As a routesetter, I can record intent and attributes when I add a route so the team has accurate context later.
- As a manager, I can find gaps by grade, wall, and style so I can plan an inclusive setting day.
- As floor staff, I can record a climber's issue report against the correct route so it reaches the setting team.
- As a climber, I can share quick feedback from a route's QR code so the gym understands how the climb felt.
- As a setting manager, I can review setter trends in comparable contexts so coaching is fair and useful.

## MVP scope

The hackathon build will demonstrate the complete data loop using a seeded gym and real-time or mocked feedback.

### Build

- Staff login with staff, setter, and floor-staff roles.
- Active-route inventory with photo, metadata, filtering, and route detail pages.
- Route creation and status changes (active, review, scheduled for strip, archived).
- QR-code/mobile feedback page for sent/tried/projecting, grade, enjoyment, and tags.
- Staff overview with wall-health distribution, review queue, and recent feedback.
- Basic reset planner and contextual setter-insight view.

### Defer

- Membership-system integrations and verified member identity.
- Push notifications, automated scheduling, and native apps.
- Multi-location organization hierarchy beyond a simple location filter.
- Complex statistical modeling and automated recommendations.

## Data model

| Entity | Important fields |
| --- | --- |
| Gym | name, locations, grade system, tag vocabulary |
| Wall | gym, name, zone, angle/type, active status |
| Route | wall, photo, identifier, setters, set date, assigned grade, styles, status, reset date |
| Feedback | route, timestamp, outcome, perceived grade, enjoyment, tags, comment, anonymized contributor ID |
| Issue report | route, type, note, timestamp, status, owner |
| Setter | staff profile, role, active status |
| Setting cycle | date range, planned walls, routes to strip, routes added |

## Metrics and definitions

| Metric | Definition | Decision it supports |
| --- | --- | --- |
| Engagement | Unique contributors and activity events over time | Keep, refresh, or strip a route |
| Grade calibration | Median perceived grade relative to assigned grade, with sample size | Reassess grade labels and team calibration |
| Enjoyment | Aggregated 1–5 rating plus feedback tags | Identify strong movement and pain points |
| Issue rate | Issue reports relative to feedback volume | Prioritize inspection or adjustment |
| Coverage | Active routes grouped by wall × grade × style | Plan a balanced setting cycle |
| Route age | Days since set, adjusted by planned reset date | Maintain a fresh rotation |

We will label insight quality as low, medium, or high based on the number and recency of responses. This makes uncertainty visible and discourages over-reading sparse data.

## Fairness, privacy, and safety principles

- **Aggregate by default.** Staff see route-level trends; individual climber activity remains private.
- **No public setter rankings.** Setter data is an internal coaching tool with contextual comparisons and sufficient-sample thresholds.
- **Separate enjoyment from difficulty.** A hard or polarizing route is not inherently poor setting.
- **Keep the human decision-maker.** Scores and flags recommend review; staff decide whether to adjust or strip a route.
- **Escalate safety feedback.** "Sharp," "broken hold," and related tags enter a visible issue queue rather than waiting for analytics review.
- **Design for diverse bodies.** Track tags such as reachy and morpho as prompts to examine route accessibility, not as automatic evidence of failure.

## Success criteria

For the hackathon demo, success means a staff member can add a route, receive climber feedback through the QR flow, and make an informed operational decision from the dashboard in under five minutes.

For a pilot gym, we would track:

- Percentage of active routes with complete metadata.
- Percentage of new routes receiving feedback in their first week.
- Time from issue report to staff acknowledgement.
- Percentage of setting cycles that use the coverage/reset planner.
- Staff-reported confidence in explaining reset decisions.

## Demo narrative

1. A routesetter adds a new V3 slab route, including a photo, intended style, and set date.
2. Climbers scan its placard QR code and quickly report sends, perceived difficulty, and feedback such as "technical" and "reachy."
3. The staff dashboard flags a meaningful difference between the assigned grade and feedback, while the wall-health view shows a gap in approachable slab routes.
4. The setting manager opens the route detail, sees the sample size and comments, and adds it to the next review cycle rather than treating the score as an automatic verdict.
5. The reset planner shows which older, low-engagement routes can be stripped to create room for the planned coverage gap.

## Why this is a strong community-impact project

Crux is built with purpose because it improves the everyday environment where a local climbing community meets. It respects climbers as contributors, gives staff a practical way to act on feedback, and avoids treating people or setters as leaderboard entries. Even a small gym can use it to make setting more intentional, inclusive, and transparent.

## Future direction

Once the MVP proves useful, Crux could add memberships-system integrations, configurable setting-cycle templates, printable QR placards, issue-notification workflows, multi-gym benchmarking with opt-in anonymized data, and accessibility-focused reporting. These extensions should remain in service of the same principle: better information should create better walls for more people.
