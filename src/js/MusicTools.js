import React, { Component } from "react";
import { BrowserRouter as Router, Routes, Route, Link, Switch } from "react-router-dom";

import NotFound from "./Error/NotFound.js";
import Progress from "./Util/circularProgress.js";
import showMessage from "./Toast.js";

import GlobalTheme from './Theme.js';

import { ThemeProvider, StyledEngineProvider } from '@mui/styles';

import {AppBar, Toolbar, IconButton, Drawer, List, Divider, ListItem, ListItemIcon, ListItemText, Typography} from '@mui/material';

import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import HomeIcon from '@mui/icons-material/Home';

import { Build, QueueMusic, ExitToApp, AccountCircle, KeyboardBackspace, GroupWork, Policy } from '@mui/icons-material'

const axios = require('axios');

import Playlists from './Playlist/AllPlaylistsRouter';

const LazyIndex = React.lazy(() => import(/* webpackChunkName: "index" */ "./Index/Index"))
const LazyPlaylists = React.lazy(() => import(/* webpackChunkName: "allPlaylists" */ "./Playlist/AllPlaylistsRouter"))
const LazyPlaylistView = React.lazy(() => import(/* webpackChunkName: "playlist" */ "./Playlist/View/PlaylistRouter"))
const LazySettings = React.lazy(() => import(/* webpackChunkName: "settings" */ "./Settings/SettingsRouter"))
const LazyAdmin = React.lazy(() => import(/* webpackChunkName: "admin" */ "./Admin/AdminRouter"))
const LazyTags = React.lazy(() => import(/* webpackChunkName: "allTags" */ "./Tag/TagRouter"))
const LazyTag = React.lazy(() => import(/* webpackChunkName: "tag" */ "./Tag/View"))

/**
 * Root component for app
 */
class MusicTools extends Component {

    constructor(props){
        super(props);
        this.state = {
            type: null,
            spotify_linked: null,
            drawerOpen: false
        }
        this.setOpen = this.setOpen.bind(this);
    }

    /**
     * Get user info from API on load
     */
    componentDidMount() {
        this.getUserInfo();
    }

    /**
     * Cancel get user info request
     */
    componentWillUnmount() {
        this.userInfoCancelToken.cancel();
    }

    /**
     * Get user info from API
     */
    getUserInfo(){
        this.userInfoCancelToken = axios.CancelToken.source();

        var self = this;
        axios.get('/api/user', {
            cancelToken: this.userInfoCancelToken.token
        })
        .then((response) => {
            self.setState({
                type: response.data.type,
                spotify_linked: response.data.spotify_linked
            })
        })
        .catch((error) => {
            showMessage(`error getting user info (${error.response.status})`);
        });
    }

    /**
     * Set whether side app drawer is open
     * @param {*} bool Open state of side drawer 
     */
    setOpen(bool){
        this.setState({
            drawerOpen: bool
        })
    }

    render(){
        return (
            (<Router>
                {/*<StyledEngineProvider injectFirst>*/}
                    <ThemeProvider theme={GlobalTheme}>

                        {/* TOP APP BAR */}

                        <AppBar position="sticky">
                            <Toolbar>
                                <IconButton
                                    edge="start"
                                    color="inherit"
                                    aria-label="menu"
                                    onClick={(e) => this.setOpen(true)}
                                    size="large">
                                <MenuIcon />
                                </IconButton>
                                <Typography variant="h6">
                                    <Link to='/app/playlists' style={{textDecoration: 'none'}}>
                                        <div className="title-small">
                                            <h1 >Mixonomer</h1>
                                        </div>
                                    </Link>
                                </Typography>
                            </Toolbar>
                        </AppBar>

                        {/* MENU DRAWER */}
                        
                        <Drawer
                            variant="persistent"
                            anchor="left"
                            open={this.state.drawerOpen}
                            onClose={(e) => this.setOpen(false)}
                        >
                            <div>
                                <IconButton onClick={(e) => this.setOpen(false)} size="large">
                                    <ChevronLeftIcon />
                                </IconButton>
                            </div>
                            <Divider />
                            <div
                            role="presentation"
                            onClick={(e) => this.setOpen(false)}
                            onKeyDown={(e) => this.setOpen(false)}
                            >
                            <List>
                                {/* PLAYLISTS */}
                                <ListItem button key="playlists" component={Link} to='/app/playlists'>
                                    <ListItemIcon><QueueMusic /></ListItemIcon>
                                    <ListItemText primary="Playlists" />
                                </ListItem>

                                {/* TAGS */}
                                <ListItem button key="tags" component={Link} to='/app/tags'>
                                    <ListItemIcon><GroupWork /></ListItemIcon>
                                    <ListItemText primary="Tags" />
                                </ListItem>

                                {/* SETTINGS */}
                                <ListItem button key="settings" component={Link} to='/app/settings/password'>
                                    <ListItemIcon><Build /></ListItemIcon>
                                    <ListItemText primary="Settings" />
                                </ListItem>

                                {/* ADMIN */}
                                { this.state.type == 'admin' &&
                                    <ListItem button key="admin" component={Link} to='/app/admin/lock'>
                                        <ListItemIcon><AccountCircle /></ListItemIcon>
                                        <ListItemText primary="Admin" />
                                    </ListItem>
                                }

                                <ListItem button key="privacy" onClick={(e) => { window.location.href = '/privacy' }}>
                                    <ListItemIcon><Policy /></ListItemIcon>
                                    <ListItemText primary="Privacy" />
                                </ListItem>

                                {/* LOGOUT */}
                                <ListItem button key="logout" onClick={(e) => { window.location.href = '/auth/logout' }}>
                                    <ListItemIcon><KeyboardBackspace /></ListItemIcon>
                                    <ListItemText primary="Logout" />
                                </ListItem>

                                {/* SARSOO.XYZ */}
                                <ListItem button key="sarsoo.xyz" onClick={(e) => { window.location.href = 'https://sarsoo.xyz' }}>
                                    <ListItemIcon><ExitToApp /></ListItemIcon>
                                    <ListItemText primary="sarsoo.xyz" />
                                </ListItem>
                            </List>
                            </div>
                        </Drawer>
                        
                        {/* ROUTER SWITCH */}

                        <div className="full-width">
                            <Routes>
                                {/*<React.Suspense fallback={<Progress/>}>*/}
                                {/*    <Route path="/app" exact component={LazyIndex} />*/}
                                    <Route path="/app/playlists" element={<Playlists/>} />
                                    {/*<Route path="/app/tags" component={LazyTags} />*/}
                                    {/*<Route path="/app/tag/:tag_id" component={LazyTag} />*/}
                                    {/*<Route path="/app/settings" component={LazySettings} />*/}
                                    {/*{ this.state.type == 'admin' && <Route path="/app/admin" component={LazyAdmin} /> }*/}
                                    {/*<Route path='/app/playlist/:name' component={LazyPlaylistView} />*/}
                                {/*</React.Suspense>*/}
                                {/*<Route component={NotFound} />*/}
                            </Routes>
                        </div>
                    </ThemeProvider>
                {/*</StyledEngineProvider>*/}
            </Router>)
        );
    }

}

export default MusicTools;