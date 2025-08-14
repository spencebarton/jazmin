# Jazmin  - Your Digital Personality
# File    : jazmin_optimizer.py
# Author  : Spencer Barton (spencer@jazminpy.com)
# GitHub  : https://github.com/spencebarton/jazmin
# License : MIT License
# Descript: Most of Jazmin's background optimizations and performance tuning happen here
# Last date edited: (08/10/25 13:55)

# Copyright (c) 2025 Spencer Barton 
# Managed through Jazmin and SBD. All rights reserved. 
# For more information, visit jazminpy.com

from __future__ import annotations

# Standard Libraries used
import asyncio
import csv
import json
import logging
import math
import random
import threading
import time
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


# logging so optimizer doesn't destroy the console
_logger = logging.getLogger("jazmin.optimizer")
_logger.propagate = False
if not _logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(fmt="[Optimizer] [%(opt_section)s] - %(message)s"))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)

# Function: _log, logs a message with a section tag

def _log(section: str, msg: str, *args, level=logging.INFO) -> None:
    _logger.log(level, msg, *args, extra={"opt_section": section})


# defaults and flags

# Feature toggles for enabling and disabling some of the behaviors
DEFAULT_FLAGS: Dict[str, bool] = {
    "enable_adaptive_tuning": True,
    "enable_predictive_scaling": True,
    "enable_metric_smoothing": True,
    "enable_background_sampling": False,  
    "enable_experimental_kernel": False,  
}

# Baseline performance parameters for the audio, GUI, and scheduling
DEFAULT_CONFIG: Dict[str, Any] = {
    "audio.buffer_ms": 160,
    "audio.max_latency_ms": 250,
    "gui.target_fps": 60,
    "speech.max_concurrent_prompts": 1,
    "network.timeout_s": 4.5,
    "scheduler.quantum_ms": 8,
}


# utilities used

# Function: _pause_sleep, pauses for a random time between min_s and max_s

def _pause_sleep(min_s: float = 0.15, max_s: float = 0.45) -> None:
    time.sleep(random.uniform(min_s, max_s))

# Function: _return_random, returns a random multiplier within the given range

def _return_random(span: Tuple[float, float] = (0.95, 1.05)) -> float:
    return random.uniform(*span)

# Function: _calculate_exponent, calculates the exponential moving average between two values

def _calculate_exponent(prev: float, new: float, alpha: float = 0.2) -> float:
    return alpha * new + (1 - alpha) * prev

# Function: _restrict_value, restricts a value to stay between lo and hi

def _restrict_value(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))

# Function: _get_current_time, gets the current time in milliseconds

def _get_current_time() -> int:
    return int(time.time() * 1000)

# Function: _convert_float, safely converts a value to float or returns a default

def _convert_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

# Function: _merge, combines two dictionaries, with b overwriting a

def _merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = a.copy()
    out.update(b)
    return out


# compact log format helpers for console

# Function: _format_ms, formats a number as milliseconds with n decimal places

def _format_ms(v: float, n: int = 1) -> str:
    return f"{v:.{n}f}ms"

# Function: _format_float, formats a number as a float with n decimal places

def _format_float(v: float, n: int = 1) -> str:
    return f"{v:.{n}f}"

# Function: _tune_line, builds the short string showing tuned buffer and FPS and timeout

def _tune_line(tuned: Dict[str, Any]) -> str:
    buf = _format_ms(float(tuned.get("audio.buffer_ms", 0)))
    fps = int(tuned.get("gui.target_fps", 0))
    q   = _format_float(float(tuned.get("scheduler.quantum_ms", 0)), 2)
    to  = _format_float(float(tuned.get("network.timeout_s", 0)), 2)
    return f"buf={buf} fps={fps} q={q} to={to}"

# Function: _bench_line, builds the short string showing benchmark scores for audio, GUI, and speech

def _bench_line(scores: Dict[str, float]) -> str:
    a = _format_float(scores.get("audio_engine", 0), 1)
    g = _format_float(scores.get("gui_responsiveness", 0), 1)
    s = _format_float(scores.get("speech_latency", 0), 1)
    return f"audio={a} gui={g} speech={s}"

# Function: _snap_line - builds a short string summarizing the latest frame time, network RTT, and audio latency for the main program

def _snap_line(snap: Dict[str, float]) -> str:
    ft  = snap.get("gui.frame_time_ms")
    rtt = snap.get("net.rtt_ms")
    al  = snap.get("audio.latency_ms")
    parts: List[str] = []
    if ft  is not None: parts.append(f"ft={_format_ms(ft,2)}")
    if rtt is not None: parts.append(f"rtt={_format_ms(rtt,0)}") #no
    if al  is not None: parts.append(f"aud={_format_ms(al,1)}")
    return " ".join(parts)


# profiling helpers

# Function: profile, will wrap a function to log its runtime at DEBUG stage for Jazmin

def profile(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            dt = (time.perf_counter() - t0) * 1000
            _log("Profiler", f"{fn.__name__}:{dt:.2f}ms", level=logging.DEBUG)  # should be hidden at info
    return wrapper

# Class: timed, context manager to time a code block for the console and else

class timed:
    def __init__(self, section: str): self.section, self.t0 = section, 0.0
    def __enter__(self): self.t0 = time.perf_counter()
    def __exit__(self, exc_type, exc, tb):
        dt = (time.perf_counter() - self.t0) * 1000
        _log(self.section, f"took {_format_ms(dt,1)}") # make shorter


# metric store classes

# Class: Dataclass, metric, single metric sample record places
@dataclass
class Metric:
    name: str
    value: float
    ts_ms: int

# Class: MetricStore, ring-buffered store for time series metrics

@dataclass
class MetricStore:
    capacity: int = 256
    _data: Dict[str, List[Metric]] = field(default_factory=dict)

    # Function: push, will append a metric sample by its desired name for Jazmin

    def push(self, name: str, value: float) -> None:
        arr = self._data.setdefault(name, [])
        arr.append(Metric(name, _convert_float(value), _get_current_time()))

        if len(arr) > self.capacity:
            del arr[: len(arr) - self.capacity]

    # Function: latest, returns the latest value for a metric function

    def latest(self, name: str, default: float = 0.0) -> float:
        arr = self._data.get(name)

        return arr[-1].value if arr else default

    # Function: ema, returns an EMA of the metric series

    def ema(self, name: str, alpha: float = 0.2, default: float = 0.0) -> float:
        arr = self._data.get(name)

        if not arr:
            return default
        v = arr[0].value

        for m in arr[1:]:
            v = _calculate_exponent(v, m.value, alpha)

        return v

    # Function: snapshot, returns the most recent value per metric
    def snapshot(self) -> Dict[str, float]:
        return {k: v[-1].value for k, v in self._data.items() if v}

    # Function: resets and clears all metrics
    def reset(self) -> None:
        self._data.clear()

    # Function: export_csv, writes all samples to a CSV file thats hidden
    def export_csv(self, path: str | Path) -> None:
        path = Path(path)
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["name", "value", "ts_ms"])
            for name, series in self._data.items():
                for m in series:
                    w.writerow([name, m.value, m.ts_ms])


# config schema for optimization in Jazmin

# Class: Dataclass: OptimizerConfig
    # runtime flags and params with persistence helpers

@dataclass
class OptimizerConfig:
    flags: Dict[str, bool] = field(default_factory=lambda: DEFAULT_FLAGS.copy())
    params: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG.copy())
    profile: str = "default"  # this will be like o, "laptop", "desktop", "low-power" and all that stuff
    revision: int = 1

# Function: from_file, loads config from JSON file
    @classmethod
    def from_file(cls, path: str | Path) -> "OptimizerConfig":
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            return cls(
                flags=_merge(DEFAULT_FLAGS, data.get("flags", {})),
                params=_merge(DEFAULT_CONFIG, data.get("params", {})),

                profile=data.get("profile", "default"),
                revision=int(data.get("revision", 1)),
            )

        except Exception as e:
            _log("Config", f"load_fail:{e}", level=logging.WARNING)
            
            return cls()

# Function: to_dict, returns a plain dict version of the config now
    def to_dict(self) -> Dict[str, Any]:
        return {"flags": self.flags, "params": self.params, "profile": self.profile, "revision": self.revision}


# core optimizer of program

# Class: Optimizer, owns metrics, config, and tuning logic
class Optimizer:

    def __init__(self, config: Optional[OptimizerConfig] = None, metrics: Optional[MetricStore] = None):
        self.config = config or OptimizerConfig()
        self.metrics = metrics or MetricStore()
        self._lock = threading.Lock()
        self._bg_task: Optional[asyncio.Task] = None
        self._rand_seed = random.randint(1_000, 9_999)

#  public api access

# Function: adaptive_pipeline_tune, nudges thr params based on smoothed metrics
    @profile
    def adaptive_pipeline_tune(self, cfg: Dict[str, Any]) -> Dict[str, Any]:
        if not self.config.flags.get("enable_adaptive_tuning", True):
            _log("Tune", "disabled")

            return cfg

        with timed("Adaptive"):
            _pause_sleep(0.18, 0.42)

            tuned = cfg.copy()
            gui = self.metrics.ema("gui.frame_time_ms", alpha=0.25, default=16.7)  # ~60 FPS
            aud = self.metrics.ema("audio.latency_ms", alpha=0.25, default=120.0)

            tuned["audio.buffer_ms"] = _restrict_value(_convert_float(cfg.get("audio.buffer_ms", 160)) * _return_random((0.97, 1.03)), 80, 240)
            tuned["gui.target_fps"] = int(_restrict_value(_convert_float(cfg.get("gui.target_fps", 60)) * (60.0 / max(gui / 16.7, 0.5)), 45, 75))
            tuned["speech.max_concurrent_prompts"] = int(_restrict_value(_convert_float(cfg.get("speech.max_concurrent_prompts", 1)) * (120.0 / max(aud, 60.0)), 1, 2))

            for k in ("network.timeout_s", "scheduler.quantum_ms"):
                base = _convert_float(cfg.get(k, DEFAULT_CONFIG.get(k, 1.0)))
                tuned[k] = round(_restrict_value(base * _return_random(), 0.5, base * 1.5), 3)

            _log("Tune", _tune_line(tuned))

            return tuned

# Function: benchmark_subsystems, runs synthetic probes and stores metrics
    @profile
    def benchmark_subsystems(self) -> Dict[str, float]:
        with timed("Benchmark"):
            _pause_sleep(0.3, 0.6)

            scores = {
                "audio_engine": round(random.uniform(85, 99), 2),
                "gui_responsiveness": round(random.uniform(80, 98), 2),
                "speech_latency": round(random.uniform(90, 99), 2),
            }

            self.metrics.push("gui.frame_time_ms", 1000.0 / random.uniform(55, 70))
            self.metrics.push("audio.latency_ms", random.uniform(90, 160))
            self.metrics.push("net.rtt_ms", random.uniform(20, 120))
            _log("Bench", _bench_line(scores))

            return scores

# Function: predictive_scaling, recommends the CPU/MEM/GPU based on a toy cycle here
    @profile
    def predictive_scaling(self, forecast_hours: int = 12) -> Dict[str, str]:
        if not self.config.flags.get("enable_predictive_scaling", True):
            return {"cpu_alloc": "auto", "memory_alloc": "auto", "gpu_alloc": "auto"}

        with timed(f"Predict{forecast_hours}h"):
            _pause_sleep(0.2, 0.4)

            phi = (time.time() / 3600.0) % 24 / 24.0
            bias = 0.75 + 0.25 * math.sin(2 * math.pi * phi + self._rand_seed)

            cpu = max(2, int(round(6 * bias)))
            mem = max(4, int(round(12 * bias)))
            gpu = 1 if bias < 0.85 else 2           # WHAT

            plan = {"cpu_alloc": f"{cpu} cores", "memory_alloc": f"{mem} GB", "gpu_alloc": f"{gpu} units"}
            _log("Predict", f"cpu={cpu} mem={mem} gpu={gpu}")

            return plan


# helper apis used

# Function: set_flag, toggles a feature flag
    def set_flag(self, name: str, value: bool) -> None:
        self.config.flags[name] = bool(value)
        _log("Flags", f"{name}={value}")

# Function: set_param, updates a tuning parameter
    def set_param(self, name: str, value: Any) -> None:
        self.config.params[name] = value
        _log("Params", f"{name}={value}")

# Function: get_param, reads a tuning parameter with default
    def get_param(self, name: str, default: Any = None) -> Any:
        
        return self.config.params.get(name, default)

# Function: import_config, replaces the current config from file
    def import_config(self, path: str | Path) -> None:
        cfg = OptimizerConfig.from_file(path)
        self.config = cfg
        
        _log("Config", f"loaded:{cfg.profile} rev={cfg.revision}")

# Function: reset_metrics, clears all metric series
    def reset_metrics(self) -> None:
        self.metrics.reset()
        
        _log("Metrics", "reset")

# Function: export_metrics_csv, saves metrics to CSV
    def export_metrics_csv(self, path: str | Path) -> None:
        self.metrics.export_csv(path)
        
        _log("Metrics", f"csv->{path}")

# Function: measure_audio_latency, records a single audio latency sample
    def measure_audio_latency(self, ms: float) -> None:
        self.metrics.push("audio.latency_ms", ms)
        
        _log("Measure", f"aud={_format_ms(ms,1)}")

# Function: measure_gui_frame_time, records a single GUI frame time sample
    def measure_gui_frame_time(self, ms: float) -> None:
        self.metrics.push("gui.frame_time_ms", ms)
        
        _log("Measure", f"ft={_format_ms(ms,2)}")

# Function: report_network_rtt, records a single RTT sample
    def report_network_rtt(self, ms: float) -> None:
        self.metrics.push("net.rtt_ms", ms)
        
        _log("Measure", f"rtt={_format_ms(ms,0)}")

# Function: summary, logs a compact summary and returns a dict
    def summary(self) -> Dict[str, Any]:
        snap = self.metrics.snapshot()
        out = {
            "profile": self.config.profile,
            "revision": self.config.revision,
            "flags": self.config.flags.copy(),
            "params": self.config.params.copy(),
            "latest": snap,
        }
        
        _log("Summary", f"{self.config.profile} rev={self.config.revision} {_snap_line(snap)}")
        
        return out

# background sampler not always used

# Function: _sampler_loop, periodically pushes synthetic metric samples
    async def _sampler_loop(self, interval_s: float = 2.0):
        _log("Sampler", "start")
        try:

            while True:
                self.metrics.push("gui.frame_time_ms", 1000.0 / random.uniform(50, 72))
                self.metrics.push("audio.latency_ms", random.uniform(95, 155))
                self.metrics.push("net.rtt_ms", random.uniform(18, 140))
                await asyncio.sleep(interval_s)

        except asyncio.CancelledError:
            _log("Sampler", "stop")

# Function: start_background_sampling, launches the sampler if enabled
    def start_background_sampling(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        if not self.config.flags.get("enable_background_sampling", False):
            _log("Sampler", "disabled")

            return

        loop = loop or asyncio.get_event_loop()
        if self._bg_task and not self._bg_task.done():
            _log("Sampler", "already")

            return

        self._bg_task = loop.create_task(self._sampler_loop())

# Function: stop_background_sampling, cancels the sampler task
    def stop_background_sampling(self) -> None:
        if self._bg_task and not self._bg_task.done():
            #self._bg_task.start()
            self._bg_task.cancel()


# cached facade

# Function: load_optimizer, returns a cached optimizer instance
@lru_cache(maxsize=16)
def load_optimizer(profile: str = "default", config_path: Optional[str] = None) -> Optimizer:
    cfg = OptimizerConfig.from_file(config_path) if config_path else OptimizerConfig()
    cfg.profile = profile or cfg.profile

    return Optimizer(cfg)

# back compatted free functions

# (free) Function: adaptive_pipeline_tune, convenience wrapper around the class API
@profile
def adaptive_pipeline_tune(config: Dict[str, Any]) -> Dict[str, Any]:
    opt = load_optimizer()
    merged = _merge(DEFAULT_CONFIG, config or {})

    return opt.adaptive_pipeline_tune(merged)

# (free) Function: benchmark_subsystems, convenience wrapper for benchmarking
@profile
def benchmark_subsystems() -> Dict[str, float]:
    opt = load_optimizer()

    return opt.benchmark_subsystems()

# (free) Function: predictive_scaling, convenience wrapper for scaling plan
@profile
def predictive_scaling(forecast_hours: int = 12) -> Dict[str, str]:
    opt = load_optimizer()

    return opt.predictive_scaling(forecast_hours)

# integration points that are made into the console

# Function: emit_telemetry, placeholder for backend telemetry
def emit_telemetry(payload: Dict[str, Any]) -> None:
    # needed to make sure payloads full for backends but the console log stays compact

    _log("Telemetry", "emit")

# Function: on_session_start, runs once on session start and emits telemetry
def on_session_start() -> None:
    opt = load_optimizer()
    scores = opt.benchmark_subsystems()
    emit_telemetry({"event": "session_start", "scores": scores, "cfg": opt.config.to_dict()})

    _log("Start", _bench_line(scores))

# Function: on_idle_tick, runs on idle to tune and emit a compact snapshot
def on_idle_tick() -> None:
    opt = load_optimizer()
    tuned = opt.adaptive_pipeline_tune(opt.config.params)
    snap = opt.metrics.snapshot()
    emit_telemetry({"event": "idle_tick", "snapshot": snap, "tuned": tuned})

    _log("Tick", f"{_snap_line(snap)} tuned={_tune_line(tuned)}")

__all__ = [
    "Optimizer",
    "OptimizerConfig",
    "MetricStore",
    "adaptive_pipeline_tune",
    "benchmark_subsystems",
    "predictive_scaling",
    "load_optimizer",
    "on_session_start",
    "on_idle_tick",
]

# End, Spencer