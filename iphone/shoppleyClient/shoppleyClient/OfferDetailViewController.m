//
//  OfferDetailViewController.m
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "OfferDetailViewController.h"

#import "SLAdditions.h"
#import "SLCurrentOffer.h"
#import "SLDataController.h"
#import "SLRedeemedOffer.h"
#import "SLTableViewDataSource.h"
#import "SLTableItem.h"

@implementation OfferDetailViewController

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if ((self = [super init])) {
        _offer = [[query objectForKey:@"offer"] retain];
        self.title = _offer.name;
           
        self.tableViewStyle = UITableViewStyleGrouped;
        self.variableHeightRows = YES;
        
        _isCurrentOffer = [_offer isKindOfClass:[SLCurrentOffer class]];
        _isLoadingOfferCode = NO;
        
        [[TTNavigator navigator].URLMap from:[self rateURL] toViewController:self selector:@selector(rateOffer)];
        [[TTNavigator navigator].URLMap from:[self feedbackURL] toViewController:self selector:@selector(feedbackOffer)];
        [[TTNavigator navigator].URLMap from:[self forwardURL] toViewController:self selector:@selector(forwardOffer)];
    }
    return self;
}

- (void)dealloc {
    [[TTNavigator navigator].URLMap removeURL:[self rateURL]];
    [[TTNavigator navigator].URLMap removeURL:[self feedbackURL]];
    [[TTNavigator navigator].URLMap removeURL:[self forwardURL]];
    TT_RELEASE_SAFELY(_offer);
    [super dealloc];
}

- (void)createModel {
    NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
    NSMutableArray* sections = [[[NSMutableArray alloc] init] autorelease];
    
    if (!_isCurrentOffer) {
        NSMutableArray* transactions = [[[NSMutableArray alloc] init] autorelease];
        [transactions addObject:[SLRightValueTableItem itemWithText:@"Price Paid" value:[NSString stringWithFormat:@"$%@", ((SLRedeemedOffer*)_offer).txnAmount]]];
        [items addObject:transactions];
        [sections addObject:@""];
        
        NSMutableArray* feedbacks = [[[NSMutableArray alloc] init] autorelease];
        [feedbacks addObject:[SLRightStarsTableItem itemWithText:@"Rate" numberOfStars:((SLRedeemedOffer*)_offer).rating URL:[self rateURL]]];
        [feedbacks addObject:[TTTableTextItem itemWithText:@"Feedback to merchant" URL:[self feedbackURL]]];
        [items addObject:feedbacks];
        [sections addObject:@""];
    }
    
    NSMutableArray* contacts = [[[NSMutableArray alloc] init] autorelease];
    NSString* callURL = [NSString stringWithFormat:@"tel://%@", _offer.phone];
    if ([[UIApplication sharedApplication] canOpenURL:[NSURL URLWithString:callURL]]) {
        [contacts addObject:[TTTableTextItem itemWithText:@"Call" URL:callURL]];
    }
    [contacts addObject:[TTTableTextItem itemWithText:@"Locate" URL:[NSString stringWithFormat:@"shoppley://map/%@/%@/%@", _offer.lat, _offer.lon, [_offer.merchantName stringByReplacingOccurrencesOfString:@" " withString:@"_"]]]];
    [items addObject:contacts];
    [sections addObject:@""];
    
    if (_isCurrentOffer) {
        NSMutableArray* redeemCode = [[[NSMutableArray alloc] init] autorelease];
        if (_offer.code) {
            [redeemCode addObject:[SLRightValueTableItem itemWithText:@"Your personal redemption code" value:_offer.code]];
        } else if (_isLoadingOfferCode) {
            [redeemCode addObject:[TTTableActivityItem itemWithText:@"Processing..."]];
        } else {
            [redeemCode addObject:[TTTableButton itemWithText:@"Request a redemption code." delegate:self selector:@selector(getOfferCodeClicked)]];
        }
        [items addObject:redeemCode];
        [sections addObject:@""];
        
        NSMutableArray* forward = [[[NSMutableArray alloc] init] autorelease];
        [forward addObject:[TTTableTextItem itemWithText:@"Forward to Friends (10 points)" URL:[self forwardURL]]];
        [items addObject:forward];
        [sections addObject:@""];
    }
    
    self.dataSource = [SLSectionedDataSource dataSourceWithItems:items sections:sections];
}

- (void)viewWillAppear:(BOOL)animated {
    [self createModel];
    
    UIView* headerView = [[[OfferDetailHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 50) offer:_offer] autorelease];
    self.tableView.tableHeaderView = headerView;
    [super viewWillAppear:animated];
}

- (NSString*)rateURL {
    return [NSString stringWithFormat:@"shoppley://offer/%@/rate", _offer.offerId];
}

- (NSString*)feedbackURL {
    return [NSString stringWithFormat:@"shoppley://offer/%@/feedback", _offer.offerId];
}

- (NSString*)forwardURL {
    return [NSString stringWithFormat:@"shoppley://offer/%@/forward", _offer.offerId];
}

- (void)rateOffer {
    TTURLAction *urlAction = [[[TTURLAction alloc] initWithURLPath:@"shoppley://offer/rate"] autorelease];
    urlAction.query = [NSDictionary dictionaryWithObject:_offer forKey:@"offer"];
    urlAction.animated = YES;
    [[TTNavigator navigator] openURLAction:urlAction];
}

- (void)feedbackOffer {
    TTURLAction *urlAction = [[[TTURLAction alloc] initWithURLPath:@"shoppley://offer/feedback"] autorelease];
    urlAction.query = [NSDictionary dictionaryWithObject:_offer forKey:@"offer"];
    urlAction.animated = YES;
    [[TTNavigator navigator] openURLAction:urlAction];
}

- (void)forwardOffer {
    TTURLAction *urlAction = [[[TTURLAction alloc] initWithURLPath:@"shoppley://offer/forward"] autorelease];
    urlAction.query = [NSDictionary dictionaryWithObject:_offer forKey:@"offer"];
    urlAction.animated = YES;
    [[TTNavigator navigator] openURLAction:urlAction];
}

- (void)getOfferCodeClicked {
    if (!_isLoadingOfferCode) {
        _isLoadingOfferCode = YES;
        [self performSelectorInBackground:@selector(getOfferCode) withObject:self];
    }
}

- (void)getOfferCode {
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    if (![[SLDataController sharedInstance] getOfferCodeForOffer:_offer]) {
        UIAlertView *alert = [[[UIAlertView alloc]
                               initWithTitle:@""
                               message:[SLDataController sharedInstance].errorString
                               delegate:self
                               cancelButtonTitle:@"OK"
                               otherButtonTitles: nil] autorelease];
        [alert show];
    }
    [self performSelectorOnMainThread:@selector(getOfferCodeDone) withObject:nil waitUntilDone:NO];
    [pool release];
}

- (void)getOfferCodeDone {
    _isLoadingOfferCode = NO;
    [self createModel];
}

@end

@implementation OfferDetailHeaderView

- (id)initWithFrame:(CGRect)frame offer:(SLOffer*)offer {
    if ((self = [super initWithFrame:frame])) {
        static const CGFloat kImageWidth = 50;
        static const CGFloat kImageHeight = 50;
        static const CGFloat kSmallMargin = 7;
        static const CGFloat kLargeMargin = 10;
        
        self.backgroundColor = [UIColor clearColor];
        
        BOOL isCurrentOffer = [offer isKindOfClass:[SLCurrentOffer class]];
        
        CGFloat top = 0;
        
        if (TTIsStringWithAnyText(offer.banner)) {
            TTImageView* bannerImg = [[[TTImageView alloc] init] autorelease];
            bannerImg.frame = CGRectMake(0, 0, 320, 50);
            bannerImg.defaultImage = [UIImage imageNamed:@"default_banner.png"];
            bannerImg.urlPath = offer.banner;
            [self addSubview:bannerImg];
            top = 50;
        }
        
        TTImageView* imageView = [[[TTImageView alloc] init] autorelease];
        imageView.urlPath = offer.img;        
        imageView.frame = CGRectMake(kSmallMargin, top + kSmallMargin, kImageWidth, kImageHeight);
        [self addSubview:imageView];
        
        CGFloat left = kSmallMargin + kImageWidth + kLargeMargin;
        
        TTStyledTextLabel* titleLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(left, top + kSmallMargin, frame.size.width - left - kSmallMargin, 100)] autorelease];
        titleLabel.font = [UIFont systemFontOfSize:17];
        NSString* title = [NSString stringWithFormat:@"<b>%@</b> by %@", offer.name, offer.merchantName];
        titleLabel.text = [TTStyledText textFromXHTML:title lineBreaks:YES URLs:YES];
        titleLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [titleLabel sizeToFit];
        titleLabel.backgroundColor = self.backgroundColor;
        [self addSubview:titleLabel];
        
        top += kSmallMargin + MAX(titleLabel.frame.size.height, kImageHeight) + kLargeMargin;
        TTStyledTextLabel* detailLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(kSmallMargin, top, frame.size.width - (2*kSmallMargin), 100)] autorelease];
        detailLabel.font = [UIFont systemFontOfSize:14];
        NSString* detail = offer.description;
        detailLabel.text = [TTStyledText textFromXHTML:detail lineBreaks:YES URLs:YES];
        detailLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [detailLabel sizeToFit];
        detailLabel.backgroundColor = self.backgroundColor;
        [self addSubview:detailLabel];
        
        top += detailLabel.frame.size.height + kSmallMargin;
        
        TTStyledTextLabel* redLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(kSmallMargin, top, frame.size.width - (2*kSmallMargin), 100)] autorelease];
        redLabel.font = [UIFont systemFontOfSize:14];
        NSString* redLabelText = @"";
        if (isCurrentOffer) {
            redLabelText = [NSString stringWithFormat:@"<span class=\"redText\"><b>Expires: %@</b></span>", [((SLCurrentOffer*)offer).expires formatFullDateTime]];
        } else {
            redLabelText = [NSString stringWithFormat:@"<span class=\"redText\"><b>Redeemed on: %@</b></span>", [((SLRedeemedOffer*)offer).redeemedOn formatFullDateTime]];
        }
        redLabel.text = [TTStyledText textFromXHTML:redLabelText lineBreaks:YES URLs:YES];
        redLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [redLabel sizeToFit];
        redLabel.backgroundColor = self.backgroundColor;
        [self addSubview:redLabel];
        
        top += redLabel.frame.size.height;
        
        /*
        if (!isCurrentOffer) {
            // Transaction Detail
            // (yod) TTStyledTextLabel doesn't support text align
            
            top += kSmallMargin;
            TTStyledTextLabel* transactionDetailLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(kSmallMargin, top, frame.size.width - (2*kSmallMargin), 100)] autorelease];
            transactionDetailLabel.font = [UIFont systemFontOfSize:14];
            NSString* transactionDetail = [NSString stringWithFormat:@"<center>Transaction Detail<br/>$%@</center>", ((SLRedeemedOffer*)offer).txnAmount];
            transactionDetailLabel.text = [TTStyledText textFromXHTML:transactionDetail lineBreaks:YES URLs:YES];
            transactionDetailLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
            [transactionDetailLabel sizeToFit];
            transactionDetailLabel.backgroundColor = self.backgroundColor;
            [self addSubview:transactionDetailLabel];
            top += transactionDetailLabel.frame.size.height;
        }
        */
        
        // Resize
        frame.size.height = top + kLargeMargin;
        self.frame = frame;
    }
    return self;
}

@end
