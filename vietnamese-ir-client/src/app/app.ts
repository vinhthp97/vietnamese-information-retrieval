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
  error: string | null = null;

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) { }

  // Search từ http://localhost:5000/api/search với query là giá trị của biến query
  search() {
    this.loading = true;
    this.error = null;
    //Kiểm tra this.query
    if (!this.query.trim()) {
      this.error = 'Vui lòng nhập nội dung.';
      this.cdr.detectChanges();
      return;
    }

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

  // search() {
  //   if (!this.query.trim()) return;

  //   this.loading = true;
  //   this.results = [];
  //   this.error = null;

  //   this.http.post<SearchResult[]>('http://localhost:5000/api/search', { query: this.query }).subscribe({
  //     next: (res) => {
  //       this.results = res;
  //       this.loading = false;
  //       this.searched = true;
  //       console.log('Search results:', this.results);
  //       console.log('Search query:', this.query);
  //       console.log('Loading state:', this.loading);
  //     },
  //     error: (err) => {
  //       this.error = 'Lỗi khi gọi API.';
  //       this.loading = false;
  //       this.searched = true;
  //     }
  //   });
  // }





}