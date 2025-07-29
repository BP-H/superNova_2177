# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

from realtime_comm.video_chat import FrameMetadata, VideoChatManager


def test_analyze_frame_stub():
    manager = VideoChatManager()
    manager.start_call(["alice"])
    meta = manager.analyze_frame("alice", b"frame")
    assert isinstance(meta, FrameMetadata)
    assert meta.emotion == "neutral"
    assert meta.lang == "en"
