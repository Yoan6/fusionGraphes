import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MentionLegaleComponent} from "./Components/mention-legale/mention-legale.component";
import {AppComponent} from "./app.component";
import {HomeComponent} from "./Components/home/home.component";
import {GraphComponent} from "./Components/graph/graph.component";

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'mention-legale/:cityWiki/:lastUpdateDATAtourisme/:lastUpdateElus', component: MentionLegaleComponent },
  { path: 'graph', component: GraphComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
