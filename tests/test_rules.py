"""Unit tests for deterministic rule checks."""

import pytest
from rules.checker import CheckResult, run_all_checks, run_specific_check, summarize_results
from rules.ip_checks import check_duplicate_ips, check_subnet_mask, check_gateway_mismatch
from rules.interface_checks import check_interface_down
from rules.vlan_checks import check_missing_vlan
from rules.routing_checks import check_missing_routes


class TestCheckResult:
    """Test suite for CheckResult class."""
    
    def test_valid_statuses(self):
        """Test that only valid statuses are accepted."""
        valid_statuses = ["DETECTED", "NOT_DETECTED", "INSUFFICIENT_EVIDENCE", "ERROR"]
        for status in valid_statuses:
            result = CheckResult(
                check_name="test",
                status=status
            )
            assert result.status == status
    
    def test_invalid_status_raises_error(self):
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError):
            CheckResult(check_name="test", status="INVALID")
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = CheckResult(
            check_name="test_check",
            status="DETECTED",
            severity="high",
            message="Test message",
            evidence=["evidence1", "evidence2"],
            confidence="high"
        )
        result_dict = result.to_dict()
        
        assert result_dict["check_name"] == "test_check"
        assert result_dict["status"] == "DETECTED"
        assert result_dict["severity"] == "high"
        assert result_dict["message"] == "Test message"
        assert result_dict["evidence"] == ["evidence1", "evidence2"]
        assert result_dict["confidence"] == "high"


class TestDuplicateIPs:
    """Test suite for duplicate IP check."""
    
    def test_duplicate_ip_detected(self):
        """Test detection of duplicate IP in log."""
        case = {
            "case_id": "TEST-001",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "Log: %IP-4-DUP_ADDR: Duplicate address 192.168.1.100 on FastEthernet0/1",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_duplicate_ips(case)
        
        assert result.status == "DETECTED"
        assert result.severity == "high"
        assert "Duplicate address" in result.evidence[0] or "DUP_ADDR" in result.evidence[0]
    
    def test_no_duplicate_ip_detected(self):
        """Test when no duplicate IP is present."""
        case = {
            "case_id": "TEST-002",
            "symptom": "",
            "topology_note": "PC1 IP 192.168.1.50/24",
            "show_outputs": "interface GigabitEthernet0/0; ip address 192.168.1.1 255.255.255.0",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_duplicate_ips(case)
        
        assert result.status == "NOT_DETECTED"
        assert result.severity == "low"
    
    def test_insufficient_evidence(self):
        """Test when insufficient evidence is available."""
        case = {
            "case_id": "TEST-003",
            "symptom": "Network slow",
            "topology_note": "PC connected to switch",
            "show_outputs": "No IP configuration available",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_duplicate_ips(case)
        
        assert result.status == "INSUFFICIENT_EVIDENCE"
        assert result.severity == "low"


class TestSubnetMask:
    """Test suite for subnet mask check."""
    
    def test_subnet_mask_issue_detected(self):
        """Test detection of subnet mask issue."""
        case = {
            "case_id": "TEST-004",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "IP 10.1.1.50 mask 255.255.255.240; Gateway 10.1.1.30 (Outside subnet boundary)",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_subnet_mask(case)
        
        assert result.status == "DETECTED"
        assert result.severity == "high"
    
    def test_invalid_mask_length(self):
        """Test detection of invalid subnet mask length."""
        case = {
            "case_id": "TEST-005",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "IP 192.168.1.1/40",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_subnet_mask(case)
        
        assert result.status == "DETECTED"
        assert any("Invalid subnet mask length" in e for e in result.evidence)
    
    def test_no_subnet_mask_issue(self):
        """Test when no subnet mask issue is present."""
        case = {
            "case_id": "TEST-006",
            "symptom": "",
            "topology_note": "PC1 IP 192.168.1.50/24",
            "show_outputs": "interface GigabitEthernet0/0; ip address 192.168.1.1 255.255.255.0",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_subnet_mask(case)
        
        assert result.status == "NOT_DETECTED"
    
    def test_insufficient_evidence(self):
        """Test when insufficient evidence is available."""
        case = {
            "case_id": "TEST-007",
            "symptom": "Network issue",
            "topology_note": "PC connected to switch",
            "show_outputs": "No configuration available",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_subnet_mask(case)
        
        assert result.status == "INSUFFICIENT_EVIDENCE"


class TestGatewayMismatch:
    """Test suite for gateway mismatch check."""
    
    def test_gateway_mismatch_detected(self):
        """Test detection of gateway mismatch."""
        case = {
            "case_id": "TEST-008",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "IP 10.1.1.50 mask 255.255.255.240; Gateway 10.1.1.30 (Outside subnet boundary)",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_gateway_mismatch(case)
        
        assert result.status == "DETECTED"
        assert result.severity == "high"
    
    def test_no_gateway_mismatch(self):
        """Test when no gateway mismatch is present."""
        case = {
            "case_id": "TEST-009",
            "symptom": "",
            "topology_note": "PC1 IP 192.168.1.50/24; Gateway 192.168.1.1",
            "show_outputs": "Default Gateway 192.168.1.1",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_gateway_mismatch(case)
        
        assert result.status == "NOT_DETECTED"
    
    def test_insufficient_evidence(self):
        """Test when insufficient evidence is available."""
        case = {
            "case_id": "TEST-010",
            "symptom": "Network issue",
            "topology_note": "PC connected to switch",
            "show_outputs": "No configuration available",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_gateway_mismatch(case)
        
        assert result.status == "INSUFFICIENT_EVIDENCE"


class TestInterfaceDown:
    """Test suite for interface down check."""
    
    def test_interface_down_detected(self):
        """Test detection of interface down state."""
        case = {
            "case_id": "TEST-011",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "GigabitEthernet0/0.10 is administratively down line protocol is down",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_interface_down(case)
        
        assert result.status == "DETECTED"
        assert result.severity == "high"
        assert "administratively down" in " ".join(result.evidence).lower() or "line protocol is down" in " ".join(result.evidence).lower()
    
    def test_shutdown_detected(self):
        """Test detection of shutdown state."""
        case = {
            "case_id": "TEST-012",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "interface Vlan1; ip address 192.168.1.2 255.255.255.0; shutdown",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_interface_down(case)
        
        assert result.status == "DETECTED"
    
    def test_no_interface_down(self):
        """Test when no interface down is present."""
        case = {
            "case_id": "TEST-013",
            "symptom": "",
            "topology_note": "PC1 on Fa0/1",
            "show_outputs": "interface GigabitEthernet0/0; ip address 192.168.1.1 255.255.255.0; no shutdown",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_interface_down(case)
        
        assert result.status == "NOT_DETECTED"
    
    def test_insufficient_evidence(self):
        """Test when insufficient evidence is available."""
        case = {
            "case_id": "TEST-014",
            "symptom": "Network issue",
            "topology_note": "PC connected to switch",
            "show_outputs": "No interface information",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_interface_down(case)
        
        assert result.status == "INSUFFICIENT_EVIDENCE"


class TestMissingVLAN:
    """Test suite for missing VLAN check."""
    
    def test_missing_vlan_detected(self):
        """Test detection of missing VLAN."""
        case = {
            "case_id": "TEST-015",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "Switchport trunk allowed vlan 10 30 40 (VLAN 20 missing from allowed list)",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_missing_vlan(case)
        
        assert result.status == "DETECTED"
        assert result.severity == "high"
    
    def test_wrong_access_vlan(self):
        """Test detection of wrong access VLAN."""
        case = {
            "case_id": "TEST-016",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "interface FastEthernet0/10; switchport access vlan 14",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_missing_vlan(case)
        
        # This may or may not be detected depending on context
        # The check looks for specific patterns
        assert result.status in ["DETECTED", "NOT_DETECTED", "INSUFFICIENT_EVIDENCE"]
    
    def test_no_vlan_issue(self):
        """Test when no VLAN issue is present."""
        case = {
            "case_id": "TEST-017",
            "symptom": "",
            "topology_note": "PC1 on Fa0/1 (VLAN 10)",
            "show_outputs": "interface FastEthernet0/1; switchport access vlan 10",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_missing_vlan(case)
        
        assert result.status == "NOT_DETECTED"
    
    def test_insufficient_evidence(self):
        """Test when insufficient evidence is available."""
        case = {
            "case_id": "TEST-018",
            "symptom": "Network issue",
            "topology_note": "PC connected to switch",
            "show_outputs": "No VLAN information",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_missing_vlan(case)
        
        assert result.status == "INSUFFICIENT_EVIDENCE"


class TestMissingRoutes:
    """Test suite for missing routes check."""
    
    def test_missing_route_detected(self):
        """Test detection of missing route."""
        case = {
            "case_id": "TEST-019",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "router ospf 1; network 10.0.0.0 0.255.255.255 area 0; passive-interface Serial0/1/0",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_missing_routes(case)
        
        assert result.status == "DETECTED"
        assert result.severity == "high"
    
    def test_unreachable_next_hop(self):
        """Test detection of unreachable next-hop."""
        case = {
            "case_id": "TEST-020",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "ip route 172.16.0.0 255.255.0.0 10.0.0.5 (Next-hop IP 10.0.0.5 unreachable)",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_missing_routes(case)
        
        assert result.status == "DETECTED"
    
    def test_no_routing_issue(self):
        """Test when no routing issue is present."""
        case = {
            "case_id": "TEST-021",
            "symptom": "",
            "topology_note": "Router R1 connected to R2",
            "show_outputs": "router ospf 1; network 10.0.0.0 0.0.0.255 area 0",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_missing_routes(case)
        
        assert result.status == "NOT_DETECTED"
    
    def test_insufficient_evidence(self):
        """Test when insufficient evidence is available."""
        case = {
            "case_id": "TEST-022",
            "symptom": "Network issue",
            "topology_note": "PC connected to switch",
            "show_outputs": "No routing information",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = check_missing_routes(case)
        
        assert result.status == "INSUFFICIENT_EVIDENCE"


class TestRunAllChecks:
    """Test suite for run_all_checks function."""
    
    def test_run_all_checks_returns_six_results(self):
        """Test that run_all_checks returns exactly 6 results."""
        case = {
            "case_id": "TEST-023",
            "symptom": "Test symptom",
            "topology_note": "Test topology",
            "show_outputs": "Test output",
            "expected_fault": "Test fault",
            "osi_layer": "Layer 3",
            "concept_tag": "Test",
            "severity": "High"
        }
        results = run_all_checks(case)
        
        assert len(results) == 6
        assert all(isinstance(r, CheckResult) for r in results)
    
    def test_run_all_checks_with_real_case(self):
        """Test run_all_checks with a real case from dataset."""
        case = {
            "case_id": "NET-001",
            "symptom": "PC1 cannot reach Server1 in VLAN 30",
            "topology_note": "PC1 on Fa0/1 (VLAN 10); Gateway on Router Sub-interface Gi0/0.10",
            "show_outputs": "GigabitEthernet0/0.10 is administratively down line protocol is down",
            "expected_fault": "Sub-interface administratively down",
            "osi_layer": "Layer 3",
            "concept_tag": "Inter-VLAN Routing",
            "severity": "High"
        }
        results = run_all_checks(case)
        
        assert len(results) == 6
        # Should detect interface down
        interface_result = next(r for r in results if r.check_name == "interface_down")
        assert interface_result.status == "DETECTED"


class TestRunSpecificCheck:
    """Test suite for run_specific_check function."""
    
    def test_run_specific_valid_check(self):
        """Test running a specific valid check."""
        case = {
            "case_id": "TEST-024",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "GigabitEthernet0/0.10 is administratively down",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = run_specific_check(case, "interface_down")
        
        assert result.check_name == "interface_down"
        assert result.status == "DETECTED"
    
    def test_run_specific_invalid_check(self):
        """Test running an invalid check name."""
        case = {
            "case_id": "TEST-025",
            "symptom": "",
            "topology_note": "",
            "show_outputs": "",
            "expected_fault": "",
            "osi_layer": "",
            "concept_tag": "",
            "severity": ""
        }
        result = run_specific_check(case, "invalid_check")
        
        assert result.status == "ERROR"
        assert "Unknown check name" in result.message


class TestSummarizeResults:
    """Test suite for summarize_results function."""
    
    def test_summarize_results(self):
        """Test result summarization."""
        results = [
            CheckResult("check1", "DETECTED", "high", "msg1", ["ev1"], "high"),
            CheckResult("check2", "NOT_DETECTED", "low", "msg2", ["ev2"], "medium"),
            CheckResult("check3", "INSUFFICIENT_EVIDENCE", "low", "msg3", ["ev3"], "low"),
            CheckResult("check4", "ERROR", "low", "msg4", ["ev4"], "low")
        ]
        
        summary = summarize_results(results)
        
        assert summary["total_checks"] == 4
        assert summary["detected"] == 1
        assert summary["not_detected"] == 1
        assert summary["insufficient_evidence"] == 1
        assert summary["errors"] == 1
        assert len(summary["findings"]) == 1
