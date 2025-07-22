import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SearchResult } from './result.model';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

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

  allData: SearchResult[] = [
    {
      title: 'Sự phát triển của truyền hình thực tế',
      description: 'Truyền hình thực tế ngày càng phổ biến trên toàn cầu và trở thành một hiện tượng văn hoá...',
      similarity: 0.75
    },
    {
      title: 'Ảnh hưởng của truyền hình thực tế đến giới trẻ',
      description: 'Bài viết phân tích tác động của các chương trình truyền hình thực tế đến giới trẻ...',
      similarity: 0.61
    },
    {
      title: 'Các chương trình truyền hình thực tế nổi bật',
      description: 'Bài viết liệt kê và mô tả một số chương trình truyền hình thực tế nổi bật...',
      similarity: 0.54
    }
  ];

  search() {
    this.results = this.allData.filter(item =>
      item.title.toLowerCase().includes(this.query.toLowerCase()) ||
      item.description.toLowerCase().includes(this.query.toLowerCase())
    );
  }
}
