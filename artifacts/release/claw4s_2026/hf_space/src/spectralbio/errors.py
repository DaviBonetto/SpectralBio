"""Typed exceptions for strict replay and verification flows."""

from __future__ import annotations


class SpectralBioError(Exception):
    """Base class for repository-scoped execution failures."""


class EnvironmentError(SpectralBioError):
    """Raised when the local runtime or filesystem is not healthy enough."""


class MissingArtifactError(SpectralBioError):
    """Raised when a required frozen artifact is absent."""


class ChecksumMismatchError(SpectralBioError):
    """Raised when an emitted or bundled file fails integrity checks."""


class SchemaValidationError(SpectralBioError):
    """Raised when a JSON payload does not satisfy the declared contract."""


class ToleranceFailureError(SpectralBioError):
    """Raised when a metric drifts beyond the allowed tolerance."""


class AssumptionViolationError(SpectralBioError):
    """Raised when a bounded contract assumption is no longer true."""


class OfflineAssetMissingError(SpectralBioError):
    """Raised when offline replay was requested without local assets."""


class ReplaySurfaceCorruptError(SpectralBioError):
    """Raised when a replay bundle exists but is incomplete or corrupt."""
