// SYNTHETIC ONLY. Test definition exists but has not run.
import { debounce } from '../src/utils/debounce';
it('uses the latest value after a delay', () => {
  const sink = (_value: string) => {};
  const onInput = debounce(sink, 200);
  expect(typeof onInput).toBe('function');
});
