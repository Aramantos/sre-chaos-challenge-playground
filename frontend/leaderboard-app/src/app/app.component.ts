import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  leaderboard: any[] = [];
  challenges = [
    {
      id: 'robust-service',
      name: 'Robust Service',
      columns: [
        { key: 'score', header: 'Sustained RPS' },
        { key: 'avg_latency', header: 'Avg Latency (ms)' },
        { key: 'uptime_percentage', header: 'Uptime %' }
      ]
    },
    {
      id: 'graceful-degradation',
      name: 'Graceful Degradation',
      columns: [
        { key: 'score', header: 'Score' }
      ]
    },
    {
      id: 'longest-upkeep',
      name: 'Longest Upkeep',
      columns: [
        { key: 'score', header: 'Uptime Duration (s)' },
        { key: 'last_downtime', header: 'Last Downtime' },
        { key: 'num_restarts', header: 'Restarts' }
      ]
    }
  ];
  currentChallenge = this.challenges[0];

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.fetchLeaderboard(this.currentChallenge.id);
  }

  fetchLeaderboard(challengeId: string): void {
    this.leaderboard = []; // Clear leaderboard data immediately
    this.http.get<any[]>(`/api/v1/leaderboard/${challengeId}`)
      .subscribe(data => {
        this.leaderboard = data;
      });
  }

  selectChallenge(challenge: any): void {
    this.currentChallenge = challenge;
    this.fetchLeaderboard(challenge.id);
  }

  // Helper function to safely get nested property values
  getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((acc, part) => acc && acc[part], obj);
  }

  getDisplayValue(entry: any, col: any): any {
    const value = this.getNestedValue(entry, col.key);
    if (col.key === 'last_downtime' && value) {
      // Format the date for display
      return new Date(value).toLocaleString(); // Or use a specific date pipe format
    }
    return value;
  }
}

