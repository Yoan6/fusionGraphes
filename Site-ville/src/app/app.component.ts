import { Component, OnInit } from '@angular/core';
import { CityService } from 'src/app/Services/city.service';
import { Observable, Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, switchMap, tap } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title: string = 'Site de votre ville';
  city: string = '';
  showGraph: boolean = false;
  private searchTerms = new Subject<string>();
  cities$: Observable<any[]> = new Observable<any[]>();
  citiesList: any[] = [];
  noCitySelected: boolean = false;
  noCityFound: boolean = false;

  constructor(private cityService: CityService) {}

  ngOnInit() {
    this.cities$ = this.searchTerms.pipe(
      debounceTime(100), // Attendre 100ms après chaque frappe avant de lancer la recherche
      distinctUntilChanged(), // Ignorer le terme de recherche si c'est le même que le précédent
      switchMap((term: string) => this.cityService.searchCities(term).pipe(
        tap(cities => this.citiesList = cities) // Stockage des résultats de la recherche
      ))
    );

    this.cities$.subscribe();
  }

  // Fonction de recherche des villes
  search(term: string): void {
    this.searchTerms.next(term);
    this.noCitySelected = false;
    this.noCityFound = false;
  }

  // Fonction de sélection d'une ville
  selectCity(cityName: string): void {
    this.city = cityName;
    this.citiesList = [];
  }

  // Fonction de soumission du formulaire qui affiche le graphe
  onSubmit() {
    // On vérifie si la ville est sélectionnée
    if (this.city === '') {
      this.noCitySelected = true;
      return;
    }

    // On vérifie que la ville sélectionnée existe
    if (!this.cityService.cityExists(this.city, this.citiesList)) {
      this.noCityFound = true;
      this.citiesList = [];
      return;
    }

    this.showGraph = true;
  }
}
