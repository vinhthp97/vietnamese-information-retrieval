import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SearchResult } from './result.model';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('vietnamese-ir-client');
  query = '';
  results: SearchResult[] = [];
  loading: boolean = false;
  error: string | null = null;

  constructor(private http: HttpClient) { }


  allData: SearchResult[] = [
    {
      id: '1',
      title: 'Sự phát triển của truyền hình thực tế',
      content: 'Truyền hình thực tế ngày càng phổ biến trên toàn cầu và trở thành một hiện tượng văn hoá...',
      similarity: 0.75
    },
    {
      id: '2',
      title: 'Ảnh hưởng của truyền hình thực tế đến giới trẻ',
      content: 'Bài viết phân tích tác động của các chương trình truyền hình thực tế đến giới trẻ...',
      similarity: 0.61
    },
    {
      id: '3',
      title: 'Các chương trình truyền hình thực tế nổi bật',
      content: 'Bài viết liệt kê và mô tả một số chương trình truyền hình thực tế nổi bật...',
      similarity: 0.54
    }
  ];

  search(): void {
    if (!this.query.trim()) return;

    this.loading = true;
    this.results = [];
    this.error = null;

    this.http.post<SearchResult[]>('/api/search', { query: this.query }).subscribe({
      next: (res) => {
        this.results = res;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Lỗi khi gọi API.';
        this.loading = false;
      }
    });
  }
}
