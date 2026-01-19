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

  searching = false;
  searchResults: any[] = [];

  constructor(private stockService: StockService) {}

  search() {
    if (!this.symbol || this.symbol.length < 2) {
      return;
    }

    this.searching = true;
    this.searchResults = [];

    this.stockService.search(this.symbol)
      .subscribe({
        next: (res: any[]) => {
          this.searchResults = res;
          this.searching = false;
        },
        error: () => {
          this.searching = false;
        }
      });
  }

  selectSymbol(sym: string) {
    this.symbol = sym;
    this.searchResults = [];
  }

  analyze() {
    if (!this.symbol) {
      this.error = 'Please enter a symbol';
      return;
    }

    this.loading = true;
    this.error = '';
    this.result = null;

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
