import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class StockService {

  private apiUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  analyze(symbol: string) {
    return this.http.get<any>(
      `${this.apiUrl}/analyze?symbol=${symbol}`
    );
  }

  search(query: string) {
    return this.http.get<any[]>(
      `${this.apiUrl}/search?q=${query}`
    );
  }
}
