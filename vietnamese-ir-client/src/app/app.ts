import { Component, signal } from '@angular/core';
import { SearchResult } from './result.model';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-root',
  imports: [FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('vietnamese-ir-client');
  query = '';
  results: SearchResult[] = [];
  loading: boolean = false;
  searched: boolean = false;
  error: string | null = null
  isExpanded: { [key: string]: boolean } = {};

  toggleExpand(id: string) {
    this.isExpanded[id] = !this.isExpanded[id];
  }

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) { }

  // Search từ http://localhost:5000/api/search với query là giá trị của biến query
  search() {
    this.results = []
    this.loading = true;
    this.error = null;
    this.searched = false;

    this.http.post<SearchResult[]>('http://localhost:5000/api/search', { query: this.query })
      .subscribe({
        next: (data) => {
          this.results = data;
          this.loading = false;
          this.searched = true;
          this.cdr.detectChanges();
        },
        error: (err) => {
          console.error(err);
          if (err.status === 404) {
            this.error = 'Không tìm thấy tài nguyên.';
          } else {
            this.error = 'An error occurred while searching.';
          }
          this.loading = false;
          this.searched = true;
          this.cdr.detectChanges();
        }
      });
  }


  clear() {
    this.query = '';
    this.loading = false
    this.error = null;
    this.searched = false;
    this.results = [];
    this.cdr.detectChanges();
  }


}