import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { StockService } from '../../services/stock';

@Component({
  selector: 'app-analyser',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './analyser.html',
  styleUrls: ['./analyser.css']
})
export class Analyser {

  symbol = '';
  result: any;
  loading = false;
  error = '';

  constructor(private stockService: StockService) {}

  analyze() {
    if (!this.symbol) {
      this.error = 'Please enter a symbol';
      return;
    }

    this.error = '';
    this.loading = true;

    this.stockService.analyze(this.symbol.toUpperCase())
      .subscribe({
        next: (res: any) => {
          this.result = res;
          this.loading = false;
        },
        error: () => {
          this.error = 'Backend error';
          this.loading = false;
        }
      });
  }
}
