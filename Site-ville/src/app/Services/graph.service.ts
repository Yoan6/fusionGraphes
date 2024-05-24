import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GraphService {

  // Url du fichier json des données du graphe
  private url = 'assets/graph_data.json';

  constructor(
    private http: HttpClient
  ) { }

  getGraphData(): Observable<any> {
    return this.http.get(this.url);
  }
}
