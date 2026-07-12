# Data and Simulation Note

This note explains how the synthetic provider data and anomaly scenarios were created for the AgentLens prototype, detailing the underlying generation rules, key assumptions, dataset schema, and known limitations.

## 1. Value Generation Methodology

The transactional values in the simulation are generated using structured business rules rather than completely random numbers. This ensures the data resembles realistic mobile financial service (MFS) behavior.

### Cash In Generation
Cash In transactions represent funds entering a provider's ecosystem. They are governed by temporal rules:
* **Weekdays (Sunday – Thursday):** Generated within the range of **600,000 – 1,000,000 BDT**.
* **Weekends (Friday – Saturday):** Generated within the range of **350,000 – 600,000 BDT**.
* *Rationale:* Weekend transaction volumes are generally lower due to reduced business and commercial activity.

### Cash Out Generation
Cash Out represents funds leaving the ecosystem. It is simulated relative to Cash In to reflect typical cash circulation:
* Cash Out values are generated close to Cash In, but with a controlled random variation.
* *Example Scenarios:*
  * **Day 1:** Cash In of `800,000 BDT` and Cash Out of `760,000 BDT` (net liquidity increase).
  * **Day 2:** Cash In of `720,000 BDT` and Cash Out of `850,000 BDT` (net liquidity decrease).
* *Rationale:* This variation creates realistic balance movements, allowing liquidity to naturally increase on some days and decrease on others.

### Ending Balance Calculation
Instead of generating the daily ending balance randomly, it is calculated dynamically using the accounting equation:

\[
\text{Today's Ending Balance} = \text{Yesterday's Ending Balance} + \text{Cash In} - \text{Cash Out}
\]

This ensures that the balance evolves logically and realistically over time, maintaining accounting consistency.

---

## 2. Assumptions Made

To simulate realistic conditions, the historical dataset relies on five core assumptions:

* **Assumption 1: Initial Liquidity Balances**
  Each provider starts with a fixed initial liquidity pool.
  | Provider | Initial Balance (BDT) |
  | :--- | :--- |
  | **bKash** | 5,000,000 |
  | **Nagad** | 4,000,000 |
  | **Rocket** | 3,000,000 |

* **Assumption 2: Weekday vs. Weekend Volumes**
  Weekday transactions have higher volumes than weekend transactions, as most business, retail, and commercial activities take place during weekdays.

* **Assumption 3: Natural Daily Fluctuation**
  Daily transactions undergo natural fluctuations. Controlled random variation is added to both Cash In and Cash Out to prevent perfectly smooth, unrealistic data lines that would make machine learning models overfit.

* **Assumption 4: Non-negative Balances**
  Balances in the historical dataset never drop below zero. If the balance drops below a predefined safety threshold, it is automatically clipped to a minimum value.
  * *Rationale:* In reality, providers would typically inject additional liquidity or transfer funds before balances could become negative.

* **Assumption 5: Independent Provider Behavior**
  Providers behave independently. Each MFS provider (bKash, Nagad, Rocket) has its own unique transaction patterns, fluctuations, and balance history.

---

## 3. Today's Transaction Dataset

Unlike the daily historical summaries, **Today's** dataset represents individual transactional records.

### Transaction Schema
Each transaction log contains the following fields:
* `Transaction_ID`: Unique identifier for the transaction.
* `Provider`: The mobile financial service provider (bKash, Nagad, or Rocket).
* `Time`: Timestamp of the transaction.
* `Cash_In`: The cash-in amount (if any).
* `Cash_Out`: The cash-out amount (if any).

### Synthetic Anomalies
* The majority of transactions are generated within a normal operational range.
* A small number of very large deposits or withdrawals are intentionally inserted as **synthetic anomalies**.
* *Rationale:* These anomalous records serve to evaluate the performance of the anomaly detection model (e.g., Isolation Forest, velocity rules).

---

## 4. Limitations

Every synthetic dataset has inherent limitations. Users and judges should keep the following constraints in mind:

* **Limitation 1: Synthetic Nature**
  The dataset is entirely synthetic and simulated. It does not contain data collected from real-world MFS providers or actual consumer behavior.
* **Limitation 2: Limited Providers**
  Only three providers (bKash, Nagad, Rocket) are modeled. The simulation does not integrate banks, card networks, or other payment networks.
* **Limitation 3: Short History**
  Only six months of historical data are available. A longer history would be required to capture macro seasonal patterns such as Eid festivals, Ramadan, or year-end financial activities.
* **Limitation 4: No Special Events**
  The simulation does not model special events, including:
  * National holidays
  * Festival seasons
  * Government policy or regulatory changes
  * Sudden economic shocks
  * Large promotional campaigns
* **Limitation 5: Lack of Inter-Provider Interaction**
  Each provider is treated independently. The dataset does not capture inter-provider dynamics, such as customers transferring funds from bKash to Nagad, or shared market demand effects.
