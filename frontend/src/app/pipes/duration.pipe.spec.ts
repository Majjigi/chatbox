import { DurationPipe } from './duration.pipe';

describe('DurationPipe', () => {
  const pipe = new DurationPipe();

  it('shows short times in milliseconds', () => {
    expect(pipe.transform(850)).toBe('850 ms');
  });

  it('shows longer times in seconds', () => {
    expect(pipe.transform(2410)).toBe('2.41 s');
  });

  it('shows a dash when there is no value', () => {
    expect(pipe.transform(null)).toBe('–');
  });
});
