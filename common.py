"""A collection of common utility functions."""


def update(ntuple, **kwargs):
    """Update named tuple."""
    return dict(ntuple._asdict(), **kwargs)
