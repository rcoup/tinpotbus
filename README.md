# TinPotBus

Gathering some data on just how often [Auckland Transport](http://www.maxx.co.nz) buses are running early or late.

### Goals

* Buses near me seem to often run 10+ minutes early, or drivers slope off and skip runs altogether. I want some numbers to prove there's a systemic problem, since my ad-hoc complaints go nowhere.
* Help other people who regularly encounter early/late/no-show buses.

### Inspiration

The name is inspired from a [TransportBlog post](http://transportblog.co.nz/2012/06/19/our-tin-pot-dictator-bus-reliability-stats/) and [Brian Rudman's column in the Herald](http://www.nzherald.co.nz/nz/news/article.cfm?c_id=1&objectid=10794616):

> Auckland Transport's latest "good news" bus-service statistics read like the electoral results of some tin-pot dictator.
> 
> Indeed, they're so fantastical any self-respecting dictator would have had them scaled down.
> 
> The transport overlords claim last month, Auckland's public bus fleet scored 99.88 per cent for "reliability" and 99.24 per cent for punctuality.

And a follow-up [comment by deserthead](http://transportblog.co.nz/2012/09/17/more-tin-pot-dictator-bus-punctuality-stats/#comment-52564):

> Birkenhead bus 99.98%  
> Saddam Hussein (1995) 99.96%  
> NZ Bus 99.94%  
> Bashar al Assad (2007) 97.60%  
> Urban Express 95.96%  

But maybe we're just all *really* unlucky or making a big deal out of nothing?

### Okay...?

But wait, we have this fancy realtime bus tracking system, right? Even though apparently, it [needs replacing](http://www.aucklandtransport.govt.nz/about-us/board-members/Board-Meetings-Minutes/Documents/Board%20reports%20December%202013/11i%20Real%20Time%20System.pdf). In the meantime, how about we just look at when buses go past bus stops and see how often they're early or late? Of *course* the times are an estimation and of *course* they don't apply everywhere, but lets have a go and see what we learn. Anyway, passengers are worried about 5+ minutes early or late, not 30 seconds.

Uses the same requests that the Maxx [Real Time Board](http://www.maxx.co.nz/) does. Acts like a browser as much as possible.

### Install & Configure

1. Clone the code
2. Create and activate a python virtualenv
3. `pip install -r requirements.txt`
4. Create `tinpotbus/tinpotbus/settings_site.py` and override any Django settings you need to.
5. `python tinpotbus/manage.py syncdb --migrate`
6. `python tinpotbus/manage.py runserver` to start the debug server
7. Head to http://localhost:8000/admin/ and create a Watch or two. Use the Stop and Route numbers from the Maxx [Real Time Board](http://www.maxx.co.nz/).
8. Run `python tinpotbus/manage.py watch_refresh` and see the options for how to update regularly (the website does it every 45 seconds fwiw). **Don't abuse the system.**
