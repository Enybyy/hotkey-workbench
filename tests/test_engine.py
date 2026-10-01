import threading
import unittest
from hotkeys import Engine, SEQUENCES

class EngineTests(unittest.TestCase):
    def test_correct_one_mapping_and_order(self):
        seen = []
        self.assertTrue(Engine(seen.append).run("1"))
        self.assertEqual([s.value for s in seen], ["left", "right", "space"])
        self.assertNotIn("|", SEQUENCES)

    def test_cancel_interrupts_wait_and_next_output(self):
        seen = []
        engine = Engine(lambda s: (seen.append(s), engine.cancel.set()))
        self.assertFalse(engine.run("t"))
        self.assertEqual(len(seen), 1)

    def test_focus_loss_prevents_following_steps(self):
        seen = []
        engine = Engine(seen.append, lambda: not seen)
        self.assertFalse(engine.run("t"))
        self.assertEqual(len(seen), 1)

    def test_paused_and_overlap_do_not_emit(self):
        engine = Engine(lambda _: self.fail("Unexpected output"))
        engine.paused = True
        self.assertFalse(engine.run("q"))
        engine.paused = False
        engine.lock.acquire()
        try:
            self.assertFalse(engine.run("q"))
        finally:
            engine.lock.release()

    def test_cooldown(self):
        engine = Engine(lambda _: None)
        self.assertTrue(engine.run("q"))
        self.assertFalse(engine.run("q"))

if __name__ == "__main__":
    unittest.main()
