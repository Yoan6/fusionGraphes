import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders, HttpResponse} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GraphService {

  // Url du fichier json des données du graphe
  private apiUrl = 'http://localhost:5000/extract';

  constructor(private http: HttpClient) { }

  extract(ville: string, code_commune: string, departement: string): Observable<any> {
    const body = {ville, code_commune, departement};
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return this.http.post<any>(`${this.apiUrl}`, body, { headers: headers });
  }

  /*exportSite(ville: string, code_commune: string, departement: string): Observable<HttpResponse<Blob>> {
    const body = { ville, code_commune, departement };
    const headers = new HttpHeaders({
      'Content-Type': 'application/json'
    });

    return this.http.post(`${this.apiUrl}/export`, body, {
      headers: headers,
      observe: 'response',
      responseType: 'blob'
    });
  }*/
}
