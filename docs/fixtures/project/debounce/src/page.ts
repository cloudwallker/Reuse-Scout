// SYNTHETIC ONLY.
import { debounce } from './utils/debounce';
export const onInput = debounce((value: string) => {
  document.title = value;
}, 200);
