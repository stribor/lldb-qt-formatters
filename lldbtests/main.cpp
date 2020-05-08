#include <QCoreApplication>
#include <QVector>
#include <QString>
#include <QList>
#include <QPointer>
#include <QSize>
#include <QSizeF>
#include <QPointF>
#include <QRect>
#include <QRectF>
#include <QUuid>
#include <QMap>
#include <QHash>
#include <QSet>

int main(int argc, char *argv[])
{
   QCoreApplication a(argc, argv);

   QString s = "Hello World";

   QVector<int> vi;
   vi << 11;
   vi << 22;
   vi << 33;

   QVector<QString> vs;
   vs << "Hello";
   vs << "World";

   QVector<QVector<QString>> vvs;
   vvs << vs;
   vvs << vs;

   QList<int> li;
   li << 11;
   li << 22;
   li << 33;

   QList<QString> ls;
   ls << "Hello";
   ls << "World";

   QList<QList<QString>> lls;
   lls << ls;
   lls << ls;

   QPointer<QCoreApplication> ap;
   ap = &a;

	QSize size(640,480);
	size.setWidth(320);
	size.setHeight(240);
	
	QSizeF sizeF(4.0,3.0);
	sizeF.setWidth(2.0);
	sizeF.setHeight(1.0);
	
	QPoint point(5,6);
	point.setX(2);
	point.setY(4);
	
	QPointF pointF(2.23, 1.2);
	pointF.setX(2.0);
	pointF.setY(1.0);
	
	QRect rect( 5, 6, 10, 20);
	rect.setX(1);
	rect.setY(2);
	rect.setSize(size);
	
	QRectF rectF( 10.0, 10.0, 40.0, 30.0);
	rectF.setX(11.0);
	rectF.setY(12.0);
	rectF.setSize(sizeF);
	
	QUuid uuid("{95465b33-5be5-4c9d-85c5-b0d62028a687}");
	QUuid uui2("{12345678-1234-5678-9abc-123456789ABC}");

	QMap<QString, QString> map;
    map["A"] = "1";
    map["B"] = "2";
    map["C"] = "3";

    QHash<QString, QString> hash;
    hash["A"] = "1";
    hash["B"] = "2";
    hash["C"] = "3";
    
    QSet<QString> set;
    set.insert("A");
    set.insert("B");
    set.insert("C");

   return a.exec();
}
