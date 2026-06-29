"""
SmartFinance Transaction Processing Bot

UiPath RPA — Executes approved financial actions, updates banking records,
processes service requests, and handles failed transaction recovery actions.

UiPath Activity Map:
  Activity Name                   | Package                     | Configuration
  --------------------------------|-----------------------------|----------------------------------------
  Get Queue Item (Action)         | UiPath.Queue                | Queue: TransactionProcessor
  Execute Action                  | UiPath.System.Activities    | Action: ${actionType}
  Update Banking Record           | UiPath.Database.Activities  | Connection: ${CBS_CONNECTION}
  Send API Request                | UiPath.WebAPI.Activities    | Endpoint: ${CORE_BANKING_API}
  Log Execution                   | UiPath.System.Activities    | Level: Info
  Write Audit Entry               | AuditLogger Robot           | Invoke via Queue
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("smartbank.robots.transaction_processing")


class ActionType(str, Enum):
    FRAUD_BLOCK = "FRAUD_BLOCK"
    FRAUD_UNBLOCK = "FRAUD_UNBLOCK"
    BILL_PAYMENT = "BILL_PAYMENT"
    BILL_SCHEDULE = "BILL_SCHEDULE"
    REFUND_INITIATE = "REFUND_INITIATE"
    DISPUTE_CREATE = "DISPUTE_CREATE"
    ACCOUNT_UPDATE = "ACCOUNT_UPDATE"
    BALANCE_TRANSFER = "BALANCE_TRANSFER"
    OVERDRAFT_APPLY = "OVERDRAFT_APPLY"
    BUDGET_SET = "BUDGET_SET"


class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RETRY = "RETRY"


@dataclass
class ActionRequest:
    action_id: str
    case_id: str
    customer_id: str
    action_type: str
    parameters: dict[str, Any]
    source: str
    approval_ref: Optional[str] = None


@dataclass
class TransactionResult:
    action_id: str
    status: str
    message: str
    transaction_ref: Optional[str] = None
    details: dict[str, Any] = None


class TransactionProcessingRobot:
    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.simulation_mode = self.config.get("simulation_mode", True)
        self.cbs_api_url = self.config.get("cbs_api_url", "https://api.smartbank.ai/v1/cbs")
        self.max_retries = int(self.config.get("max_retries", 3))

    def execute(self, request: ActionRequest) -> TransactionResult:
        action_type = request.action_type
        status = ExecutionStatus.SUCCESS
        message = ""
        txn_ref = None
        details = {}

        try:
            if action_type == ActionType.FRAUD_BLOCK.value:
                result = self._block_card(request.parameters)
            elif action_type == ActionType.FRAUD_UNBLOCK.value:
                result = self._unblock_card(request.parameters)
            elif action_type == ActionType.BILL_PAYMENT.value:
                result = self._process_bill_payment(request.parameters)
            elif action_type == ActionType.BILL_SCHEDULE.value:
                result = self._schedule_payment(request.parameters)
            elif action_type == ActionType.REFUND_INITIATE.value:
                result = self._initiate_refund(request.parameters)
            elif action_type == ActionType.DISPUTE_CREATE.value:
                result = self._create_dispute(request.parameters)
            elif action_type == ActionType.ACCOUNT_UPDATE.value:
                result = self._update_account(request.parameters)
            elif action_type == ActionType.BALANCE_TRANSFER.value:
                result = self._transfer_balance(request.parameters)
            elif action_type == ActionType.OVERDRAFT_APPLY.value:
                result = self._apply_overdraft(request.parameters)
            elif action_type == ActionType.BUDGET_SET.value:
                result = self._set_budget(request.parameters)
            else:
                result = {"status": "FAILED", "message": f"Unknown action type: {action_type}"}

            status = ExecutionStatus(result.get("status", "FAILED"))
            message = result.get("message", "")
            txn_ref = result.get("transaction_ref", str(uuid.uuid4()))
            details = result

        except Exception as e:
            status = ExecutionStatus.FAILED
            message = f"Execution error: {str(e)}"
            logger.error(f"Transaction processing failed: {e}")

        self._log_execution(request.case_id, request.action_id, action_type, status.value)

        return TransactionResult(
            action_id=request.action_id,
            status=status.value,
            message=message,
            transaction_ref=txn_ref,
            details=details,
        )

    def _block_card(self, params: dict) -> dict:
        card_number = params.get("card_number", "XXXX")
        reason = params.get("reason", "Fraud detected")
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": f"Card {card_number[-4:]} blocked: {reason}",
                "transaction_ref": f"BLK-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/card/block", params)

    def _unblock_card(self, params: dict) -> dict:
        card_number = params.get("card_number", "XXXX")
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": f"Card {card_number[-4:]} unblocked",
                "transaction_ref": f"UNB-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/card/unblock", params)

    def _process_bill_payment(self, params: dict) -> dict:
        biller = params.get("biller", "Unknown")
        amount = params.get("amount", 0)
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": f"Bill payment of Rs.{amount} to {biller} completed",
                "transaction_ref": f"PAY-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/payment/bill", params)

    def _schedule_payment(self, params: dict) -> dict:
        biller = params.get("biller", "Unknown")
        date = params.get("scheduled_date", "TBD")
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": f"Payment to {biller} scheduled for {date}",
                "transaction_ref": f"SCH-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/payment/schedule", params)

    def _initiate_refund(self, params: dict) -> dict:
        merchant = params.get("merchant", "Unknown")
        amount = params.get("amount", 0)
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": f"Refund of Rs.{amount} initiated from {merchant}",
                "transaction_ref": f"REF-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/refund/initiate", params)

    def _create_dispute(self, params: dict) -> dict:
        txn_id = params.get("transaction_id", "Unknown")
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": f"Dispute created for transaction {txn_id}",
                "transaction_ref": f"DSP-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/dispute/create", params)

    def _update_account(self, params: dict) -> dict:
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": "Account record updated successfully",
                "transaction_ref": f"UPD-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("PUT", "/account/update", params)

    def _transfer_balance(self, params: dict) -> dict:
        amount = params.get("amount", 0)
        source = params.get("from_account", "Savings")
        target = params.get("to_account", "Current")
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": f"Rs.{amount} transferred from {source} to {target}",
                "transaction_ref": f"TRF-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/account/transfer", params)

    def _apply_overdraft(self, params: dict) -> dict:
        amount = params.get("amount", 0)
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": f"Overdraft of Rs.{amount} approved",
                "transaction_ref": f"ODR-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/overdraft/apply", params)

    def _set_budget(self, params: dict) -> dict:
        if self.simulation_mode:
            return {
                "status": "SUCCESS",
                "message": "Budget plan saved successfully",
                "transaction_ref": f"BDG-{uuid.uuid4().hex[:8].upper()}",
            }
        return self._call_cbs_api("POST", "/budget/set", params)

    def _call_cbs_api(self, method: str, path: str, data: dict) -> dict:
        import requests
        try:
            resp = requests.request(
                method,
                f"{self.cbs_api_url}{path}",
                json=data,
                timeout=30,
            )
            return resp.json()
        except Exception as e:
            logger.error(f"CBS API call failed: {e}")
            return {"status": "FAILED", "message": f"API error: {str(e)}"}

    def _log_execution(self, case_id: str, action_id: str, action_type: str, status: str):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "case_id": case_id,
            "action_id": action_id,
            "action_type": action_type,
            "status": status,
            "robot": "TransactionProcessingBot",
        }
        logger.info(f"Transaction execution logged: {json.dumps(log_entry)}")
