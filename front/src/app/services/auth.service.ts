import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { map, tap } from 'rxjs/operators';
import { User } from '../models/user';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private rootUrl = "http://localhost:8000/api/auth/";
    isLoggedIn: boolean;
    user: User;

    constructor(private http: HttpClient) {
        this.getAuthUser().subscribe(res => {
            if(res instanceof User){
                this.user = res;
                this.isLoggedIn = true;
            }
            else
                this.isLoggedIn=false;      
        })
    }

    login(email: string, password: string) {
        return this.http.post<User>(this.rootUrl + 'login', { email, password }).pipe(
            tap((user) => {
                this.user = user;
                this.isLoggedIn = true;
            })
        )
    }

    logout() {
        return this.http.post(this.rootUrl + 'logout', "").pipe(
            tap(() => this.isLoggedIn = false)
        )
    }

    isloggedIn() {
        return this.http.get<{ isAuthenticated: boolean }>(this.rootUrl + 'session').pipe(
            map(res => res.isAuthenticated)
        )
    }

    emailExists(email: string) {
        return this.http.post<any>(this.rootUrl + "emailexists", { email }).pipe(map(res => res.exists == 'true'))
    }

    getAuthUser() {
        return this.http.get<User|{isAuthenticated:boolean}>(this.rootUrl + 'getauthuser');
    }

    signUp(email:string,username:string,password:string){
        return this.http.post(this.rootUrl+'signup', {email,username,password})
    }
}
