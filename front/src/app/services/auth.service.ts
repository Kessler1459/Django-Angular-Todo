import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import {  map, switchMap, tap } from 'rxjs/operators';
import { User } from '../models/user';
import { CookieService } from 'ngx-cookie';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private rootUrl = "http://localhost:8000/api/auth/";
    token:string;
    user: User|null;

    constructor(private http: HttpClient, private cookieService:CookieService) {
        this.token=this.cookieService.get('token');
    }

    login(email: string, password: string) {
        return this.http.post<{Token: string}>(this.rootUrl + 'login', { email, password }).pipe(
            tap(res=>{
                this.setToken(res.Token)
            }),
            switchMap(()=>this.getAuthUser())
        ) 
    }

    logout() {
        return this.http.post(this.rootUrl + 'logout', "").pipe(
            tap(() => {
                this.token = "";
                this.cookieService.remove("token");
                this.user=null;
            })
        )
    }

    emailExists(email: string) {
        return this.http.post<any>(this.rootUrl + "emailexists", { email }).pipe(map(res => res.exists == 'true'))
    }

    getAuthUser() {
        return this.http.get<any>(this.rootUrl + 'user').pipe(
            tap(user=>this.user=user)
        )
    }

    signUp(email: string, username: string, password: string) {
        return this.http.post(this.rootUrl + 'signup', { email, username, password })
    }

    private setToken(token:string){
        this.cookieService.put('token',token);
        this.token=token;
    }
}
