import { Pipe, PipeTransform } from '@angular/core';

/**
 * Formats milliseconds for people to read: 850 → "850 ms", 2410 → "2.41 s".
 *
 * A pipe transforms a value inside a template: `{{ stats.totalMs | duration }}`
 */
@Pipe({
  name: 'duration',
})
export class DurationPipe implements PipeTransform {
  transform(milliseconds: number | null | undefined): string {
    if (milliseconds == null) {
      return '–';
    }
    if (milliseconds < 1000) {
      return `${milliseconds} ms`;
    }
    return `${(milliseconds / 1000).toFixed(2)} s`;
  }
}
