//
//  RedeemedOffersViewController.m
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "RedeemedOffersViewController.h"

#import "SLRedeemedOffer.h"
#import "SLTableViewDataSource.h"

@implementation RedeemedOffersViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.title = @"Redeemed Offers";
        self.tabBarItem = [[[UITabBarItem alloc] initWithTitle:self.title image:[UIImage imageNamed:@"tab_redeemed_offers.png"] tag:0] autorelease];
        
        self.tableViewStyle = UITableViewStylePlain;
        self.variableHeightRows = YES;
    }
    return self;
}

- (void)createModel {
    _offers = [[[SLDataController sharedInstance] obtainRedeemedOffersWithDelegate:self forcedDownload:NO] retain];
    
    if (_offers) {
        TTDPRINT(@"%@", _offers);
        NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
        for (int i = 0; i < [_offers count]; i++) {
            SLRedeemedOffer* offer = [_offers objectAtIndex:i];
            [items addObject:[SLRedeemedOfferTableItem itemWithOffer:offer URL:nil]];
        }
        self.dataSource = [SLListDataSource dataSourceWithItems:items];
    } else {
        self.dataSource = [TTListDataSource dataSourceWithObjects:
                           [TTTableActivityItem itemWithText:@"Processing..."],
                           nil];
    }
}

@end
