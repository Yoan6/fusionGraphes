import {Component, OnInit} from '@angular/core';
import {Observable, Subject} from "rxjs";
import {CityService} from "../../Services/city.service";
import {GraphService} from "../../Services/graph.service";
import {Router} from "@angular/router";
import {debounceTime, distinctUntilChanged, switchMap, tap} from "rxjs/operators";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  city: string = '';
  city_wiki: string = '';   // Permet d'avoir la ville avec le département pour les homonymes (Wikipédia)
  code_commune: string = '';
  departement: string = '';
  selectedCity: any = null;
  showGraph: boolean = false;
  private searchTerms = new Subject<string>();
  cities$: Observable<any[]> = new Observable<any[]>();
  citiesList: any[] = [];
  noCitySelected: boolean = false;
  noCityFound: boolean = false;
  is_an_homonyme: boolean = false;
  graphData: any = null;
  loading: boolean = false;

  constructor(
    private cityService: CityService,
    private graphService: GraphService,
    private router: Router
  ) {}

  ngOnInit() {
    this.cities$ = this.searchTerms.pipe(
      debounceTime(50),
      distinctUntilChanged(),
      switchMap((term: string) => this.cityService.searchCities(term).pipe(
        tap(cities => {
          this.citiesList = cities;
          if (cities.length === 0) {
            this.noCityFound = true;
          } else {
            this.noCityFound = false;
          }
        })
      ))
    );
    this.cities$.subscribe();
  }

  search(term: string): void {
    this.searchTerms.next(term);
    this.noCitySelected = false;
    this.noCityFound = false;
    this.is_an_homonyme = false;
    this.selectedCity = null;
  }

  selectCity(city: any): void {
    this.is_an_homonyme = this.isHomonyme(city);

    if (this.is_an_homonyme) {
      this.city = city.nom + ' (' + city.departement.nom + ')';
    } else {
      this.city = city.nom;
    }

    this.code_commune = city.code;
    this.departement = city.departement.nom;
    this.selectedCity = city;
    this.citiesList = [];
  }

  isHomonyme(city: any): boolean {
    let matchingCities = this.citiesList.filter((c: { nom: string; }) => c.nom.toLowerCase() === city.nom.toLowerCase());
    if (matchingCities.length > 1) {
      return true;
    }
    return false;
  }

  onSubmit() {
    if (this.city === '') {
      this.noCitySelected = true;
      return;
    }

    const cityName = this.city.split(' (')[0];
    this.cityService.searchCities(cityName).subscribe(cities => {
      const matchingCities = cities.filter((c: { nom: string; }) => c.nom.toLowerCase() === cityName.toLowerCase());

      if (matchingCities.length === 0) {
        this.noCityFound = true;
        this.citiesList = [];
        return;
      }

      if (matchingCities.length > 1 && !this.selectedCity) {
        this.is_an_homonyme = true;
        return;
      }

      let matchingCity: any;
      if (this.selectedCity) {
        matchingCity = matchingCities.find((c: { code: string; }) => c.code === this.selectedCity.code);
      } else {
        matchingCity = matchingCities[0];
      }

      this.noCityFound = false;
      this.is_an_homonyme = false;
      this.loading = true;
      this.code_commune = matchingCity.code;
      this.departement = matchingCity.departement.nom;
      this.citiesList = [];

      if (matchingCities.length > 1) {
        this.city = `${matchingCity.nom} (${matchingCity.departement.nom})`;
      } else {
        this.city = matchingCity.nom;
      }
      this.generateGraph();
    }, error => {
      console.log('Erreur lors de la vérification de la ville : ', error);
      this.loading = false;
    });
  }

  generateGraph() {
    this.city_wiki = this.city;
    this.is_an_homonyme = false;
    this.loading = true;
    const cityName = this.city.split(' (')[0];
    this.graphService.extract(cityName, this.code_commune, this.departement).subscribe(response => {
      if (response.status === 'success') {
        this.loading = false;
        this.graphData = response.data;
        this.showGraph = true;
        this.router.navigate(['/graph'], { state: { data: this.graphData, cityWiki: this.city_wiki } });
      } else {
        console.error('Erreur lors de la génération du graphe : ', response.message);
        this.loading = false;
        this.noCityFound = true;
      }
    }, error => {
      console.log('Erreur lors de la génération du graphe : ', error);
      this.loading = false;
    });
  }
}
