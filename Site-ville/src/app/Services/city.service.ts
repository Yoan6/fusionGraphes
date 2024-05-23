import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CityService {
  private apiUrl = 'https://geo.api.gouv.fr/communes';

  constructor(
    private http: HttpClient
  ) { }

  // Fonction de recherche des villes pour l'autocomplétion
  searchCities(name: string): Observable<any> {
    const url = `${this.apiUrl}?nom=${name}&fields=nom,code&boost=population&limit=5`;
    return this.http.get(url);
  }
}
