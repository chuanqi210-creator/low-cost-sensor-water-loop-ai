from water_ai.agents.field_data_interface_agent import FieldDataInterfaceAgent
from water_ai.domain import SensorReading


def test_field_data_interface_agent_accepts_complete_template_package() -> None:
    report = FieldDataInterfaceAgent(
        datasets=_complete_package(),
        data_origin="synthetic",
        minimum_records={
            "sensor_timeseries": 3,
            "offline_lab_results": 3,
            "catalyst_lifecycle": 2,
            "campaign_operation_log": 3,
            "cost_deployment": 2,
        },
    ).run([])

    readiness = report.metrics["readiness"]
    statuses = report.metrics["table_statuses"]
    tasks = report.metrics["calibration_tasks"]

    assert readiness["interface_status"] == "template_ready_not_field_validated"
    assert readiness["calibration_readiness_score"] >= 0.9
    assert all(status["status"] == "import_ready" for status in statuses.values())
    assert tasks[0]["task_id"] == "P1_sensor_noise_drift"
    assert "[]" not in " ".join(report.recommendations)
    assert report.issues[-1].issue_type == "synthetic_template_not_field_validated"


def test_field_data_interface_agent_blocks_missing_lab_results() -> None:
    package = _complete_package()
    package.pop("offline_lab_results")

    report = FieldDataInterfaceAgent(
        datasets=package,
        data_origin="field",
        minimum_records={
            "sensor_timeseries": 3,
            "offline_lab_results": 3,
            "catalyst_lifecycle": 2,
            "campaign_operation_log": 3,
            "cost_deployment": 2,
        },
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["interface_status"] == "schema_blocked"
    assert "offline_lab_results" in readiness["missing_tables"]
    assert report.issues[0].issue_type == "missing_field_data_table"
    assert report.metrics["calibration_tasks"][1]["task_ready"] is False


def test_field_data_interface_agent_detects_orphan_reference_batches() -> None:
    package = _complete_package()
    package["offline_lab_results"].append(
        {
            "batch_id": "B999",
            "sample_time_min": 30,
            "analyte": "COD",
            "value": 42.0,
            "unit": "mg/L",
            "method": "HACH",
            "qa_flag": "pass",
        }
    )

    report = FieldDataInterfaceAgent(
        datasets=package,
        data_origin="field",
        minimum_records={
            "sensor_timeseries": 3,
            "offline_lab_results": 3,
            "catalyst_lifecycle": 2,
            "campaign_operation_log": 3,
            "cost_deployment": 2,
        },
    ).run([])

    linkage = report.metrics["linkage_checks"]

    assert "B999" in linkage["orphan_reference_batches"]
    assert any(issue.issue_type == "orphan_reference_batches" for issue in report.issues)


def test_field_data_interface_agent_can_build_sensor_table_from_readings() -> None:
    readings = [
        SensorReading(
            timestamp_min=0,
            cycle_id=0,
            values={
                "pH": 7.1,
                "ORP_mV": 410.0,
                "EC_uScm": 1200.0,
                "turbidity_NTU": 12.0,
                "temp_C": 25.0,
                "flow_Lmin": 1.1,
                "UV254_abs": 0.7,
            },
        )
    ]
    report = FieldDataInterfaceAgent(datasets={}, data_origin="synthetic").run(readings)

    assert report.metrics["table_statuses"]["sensor_timeseries"]["record_count"] == 1
    assert report.metrics["readiness"]["interface_status"] == "schema_blocked"


def test_field_data_interface_schema_covers_r4b_guardrail_fields() -> None:
    schema = FieldDataInterfaceAgent.schema_contract()
    schema_fields = {
        field
        for spec in schema.values()
        for field in list(spec["required_fields"]) + list(spec["optional_fields"])
    }

    assert {
        "proxy_holdout_label",
        "regeneration_event",
        "tank_storage_margin",
        "actuator_latency_p90",
        "pump_valve_result",
        "hold_time_min",
    }.issubset(schema_fields)


def test_field_data_interface_schema_covers_r8e_pressure_headloss_fields() -> None:
    schema = FieldDataInterfaceAgent.schema_contract()
    schema_fields = {
        field
        for spec in schema.values()
        for field in list(spec["required_fields"]) + list(spec["optional_fields"])
    }

    assert "site_topology_or_bed_geometry" in schema
    assert {
        "pressure_drop_kPa",
        "headloss_kPa_per_m",
        "flow_normalized_pressure_residual",
        "bed_depth_m",
        "bed_area_m2",
        "nominal_HRT_min",
        "expected_clean_bed_pressure_drop_kPa",
    }.issubset(schema_fields)


def _complete_package() -> dict[str, list[dict[str, object]]]:
    return {
        "sensor_timeseries": [
            _sensor("B001", 0),
            _sensor("B001", 5),
            _sensor("B002", 0),
        ],
        "offline_lab_results": [
            _lab("B001", 5, "COD", 38.2),
            _lab("B001", 5, "target_pollutant_proxy", 0.18),
            _lab("B002", 5, "COD", 41.1),
        ],
        "catalyst_lifecycle": [
            _catalyst("C01", "B001", 12),
            _catalyst("C01", "B002", 15),
        ],
        "campaign_operation_log": [
            _operation("B001", "hold_for_validation", 0, 30),
            _operation("B001", "recirculate", 30, 90),
            _operation("B002", "release", 90, 92),
        ],
        "site_topology_or_bed_geometry": [
            {
                "site_id": "SYNTH_SITE",
                "node_id": "N3_catalyst_bed",
                "zone": "catalyst_bed",
                "upstream_node_id": "N2_reactor_mid",
                "downstream_node_id": "N4_recirculation_loop",
                "bed_id": "BED_A",
                "bed_depth_m": 0.8,
                "bed_area_m2": 0.12,
                "nominal_flow_Lmin": 1.2,
                "nominal_HRT_min": 24,
                "expected_clean_bed_pressure_drop_kPa": 2.1,
            }
        ],
        "cost_deployment": [
            {
                "item_id": "sensor_uv254",
                "category": "sensor",
                "unit_cost_cny": 4200,
                "quantity": 1,
                "lead_time_days": 7,
            },
            {
                "item_id": "catalyst_module",
                "category": "catalyst",
                "unit_cost_cny": 12000,
                "quantity": 2,
                "lead_time_days": 21,
            },
        ],
    }


def _sensor(batch_id: str, timestamp_min: int) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "timestamp_min": timestamp_min,
        "cycle_id": timestamp_min // 12,
        "pH": 7.2,
        "ORP_mV": 420.0,
        "EC_uScm": 1350.0,
        "turbidity_NTU": 18.0,
        "temp_C": 25.0,
        "flow_Lmin": 1.2,
        "UV254_abs": 0.82,
    }


def _lab(batch_id: str, sample_time_min: int, analyte: str, value: float) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "sample_time_min": sample_time_min,
        "analyte": analyte,
        "value": value,
        "unit": "mg/L",
        "method": "synthetic_reference",
        "qa_flag": "pass",
    }


def _catalyst(catalyst_id: str, batch_id: str, cycle_count: int) -> dict[str, object]:
    return {
        "catalyst_id": catalyst_id,
        "batch_id": batch_id,
        "cycle_count": cycle_count,
        "regen_count": 1,
        "activity_assay": 0.82,
        "pressure_drop_kPa": 4.5,
        "lifetime_fraction": 0.74,
    }


def _operation(batch_id: str, action_id: str, start_min: int, end_min: int) -> dict[str, object]:
    return {
        "campaign_id": "CP001",
        "batch_id": batch_id,
        "action_id": action_id,
        "start_min": start_min,
        "end_min": end_min,
        "intake_fraction": 0.75,
        "success": True,
    }
