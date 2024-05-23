import { Component } from '@angular/core';
import { CityService } from 'src/app/Services/city.service';
import { Observable, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title: string = 'Site de votre ville';
  city: string = '';
  showGraph: boolean = false;
  private searchTerms = new Subject<string>();
  cities$: Observable<any>;

  constructor(private cityService: CityService) {
    this.cities$ = this.searchTerms.pipe(
      debounceTime(100),
      distinctUntilChanged(),
      switchMap((term: string) => this.cityService.searchCities(term))
    );
  }

  // Fonction de recherche des villes
  search(term: string): void {
    this.searchTerms.next(term);
  }

  // Fonction de sélection d'une ville
  selectCity(cityName: string): void {
    this.city = cityName;
    this.searchTerms.next('');
  }

  // Fonction de soumission du formulaire qui affiche le graphe
  onSubmit() {
    // On vérifie si la ville est sélectionnée
    if (this.city === '') {
      alert('Veuillez sélectionner une ville');
      return;
    }
    // On vérifie que la ville sélectionnée est bien une ville
    this.showGraph = true;
  }
}
