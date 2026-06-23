from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state
from water_ai.simulation import generate_low_cost_sensor_stream


def test_data_quality_agent_detects_injected_faults() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    report = DataQualityAgent().run(readings)

    issue_types = {issue.issue_type for issue in report.issues}
    sensors = {issue.sensor for issue in report.issues}

    assert "missing" in issue_types
    assert "spike" in issue_types
    assert "flatline" in issue_types
    assert "drift_suspected" in issue_types
    assert "sustained_shift" in issue_types
    assert "ORP_mV" in sensors
    assert "pH" in sensors
    assert "EC_uScm" in sensors
    assert "turbidity_NTU" in sensors
    assert "flow_Lmin" in sensors
    assert report.confidence < 0.9
    assert report.metrics["sensor_scores"]["EC_uScm"] < 0.8
    assert report.metrics["sensor_scores"]["turbidity_NTU"] < 0.8
    assert report.metrics["sensor_scores"]["flow_Lmin"] < 0.8


def test_data_quality_agent_passes_clean_stream() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=False)
    report = DataQualityAgent().run(readings)

    assert report.metrics["critical_count"] == 0
    assert report.confidence >= 0.9
    assert min(report.metrics["sensor_scores"].values()) >= 0.9


def test_data_quality_agent_detects_short_window_low_flow() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("sensor_faults"), n=24, seed=7)
    report = DataQualityAgent().run(readings)
    issue_types = {issue.issue_type for issue in report.issues}
    assert "low_flow_absolute" in issue_types
