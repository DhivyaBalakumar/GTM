---
title: "The Complete HubSpot CRM Guide"
subtitle: "From pushing your first record to running a revenue engine: data model, imports, API, webhooks, automation, every hub, reporting, governance and RevOps playbooks"
date: "Edition: November 2026"
---

# How to Use This Guide

This guide explains how HubSpot works, from the ground up. It starts with what a CRM is, then covers
how data gets **into** HubSpot (by hand, imports, forms, integrations, the API, webhooks), what
HubSpot does with that data (lists, workflows, the Marketing, Sales, Service, Content and Commerce
hubs, AI), and how to report on it, govern it and design a whole revenue operation around it.

## Who it is for

- **Beginners** who have never used a CRM: read Part I, then Chapters 4 to 6, in order.
- **GTM engineers and RevOps people** who need to move data in and out reliably: Part II
  (Chapters 4 to 12) is the core, with complete API examples and a runnable pipeline.
- **Admins and team leads**: Parts III and IV cover the hubs, reporting, permissions and
  governance.
- **Interview preparation**: Chapter 22 has 40 interview questions with model answers, and the
  Appendix has cheat sheets and a glossary.

## How the book is organised

| Part | Chapters | What you get |
| --- | --- | --- |
| I. Foundations | 1–3 | What HubSpot is, the data model, properties |
| II. Getting data in (and out) | 4–12 | Every entry point, imports, forms and tracking, integrations, the API in depth, webhooks, an end-to-end push pipeline, data quality |
| III. Using your data | 13–18 | Segments, workflows, Marketing Hub, Sales Hub, Service Hub, Content, Commerce and AI |
| IV. Running HubSpot | 19–22 | Reporting, administration and security, RevOps architecture, troubleshooting and interviews |
| Appendix | — | Cheat sheets and glossary |

## The running example

The whole book uses one fictional company, **Northwind Analytics**, a B2B SaaS business that
sells analytics software to mid-market companies. Its customers and prospects use example domains
such as `acme-logistics.com` and `peopleco.de`. Seeing the same company in every chapter shows
how the pieces connect.

## A note on accuracy

HubSpot changes often: menu labels move, features get renamed, plan limits change, and the
developer platform changes (for example, since October 2026 new legacy private apps can't be
created, and API access to your own account uses **service keys**). Where this guide gives a limit
or a menu path, check it against the current
[HubSpot Knowledge Base](https://knowledge.hubspot.com) and
[developer documentation](https://developers.hubspot.com/docs) before you rely on it. The concepts,
patterns and habits here last much longer than any one menu label.

The companion code for Chapter 11 is in the `code/` folder next to this guide.
