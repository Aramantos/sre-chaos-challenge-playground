import { Component, OnInit } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, DatePipe],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'local-tracker-app';
  trackingData: any[] = [];
  userId: string = 'local-tester'; // Hardcoded for now, will be dynamic later
  expandedRunId: number | null = null;
  selectedTarget: string = '';

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.fetchTrackingData(this.userId);
  }

  fetchTrackingData(userId: string): void {
    this.trackingData = []; // Clear data immediately
    this.http.get<any>(`/api/track/${userId}`)
      .subscribe(data => {
        this.trackingData = Object.keys(data).map(target_app => {
          const sessions = data[target_app];
          return {
            target_app: target_app,
            sessions: Object.keys(sessions).map(session_id => {
              return { session_id: session_id, runs: sessions[session_id] };
            })
          };
        });
      });
  }

  toggleRunDetails(runId: number): void {
    if (this.expandedRunId === runId) {
      this.expandedRunId = null; // Collapse if already expanded
    } else {
      this.expandedRunId = runId; // Expand this run
    }
  }

  recordSession(): void {
    this.http.post('/api/record', {})
      .subscribe(response => {
        console.log(response);
      });
  }
}
